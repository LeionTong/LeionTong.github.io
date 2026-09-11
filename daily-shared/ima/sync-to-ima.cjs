#!/usr/bin/env node
/**
 * GitHub 每日优质项目简报 -> ima 知识库同步脚本
 *
 * 用法:
 *   node sync-to-ima.cjs --file "<md 文件绝对路径>" [--kb "<知识库名称>"]
 *
 * 缺省知识库名称: Daily-Github
 * 输出: 单行 JSON 到 stdout { ok, title, kb_name, media_id, message }
 * 失败: 非 0 退出码，错误信息写 stderr
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

// 通用化：依赖脚本与本脚本同目录部署（ima/ 整目录自包含），不绑定任何特定应用目录
const IMA_SKILL_DIR = __dirname;
const IMA_API = path.join(IMA_SKILL_DIR, 'ima_api.cjs');
const PREFLIGHT = path.join(IMA_SKILL_DIR, 'knowledge-base', 'scripts', 'preflight-check.cjs');
const COS_UPLOAD = path.join(IMA_SKILL_DIR, 'knowledge-base', 'scripts', 'cos-upload.cjs');

const DEFAULT_KB_NAME = 'Daily-Github';

function fail(msg) {
  process.stderr.write(JSON.stringify({ ok: false, message: msg }) + '\n');
  process.exit(1);
}

function parseArgs(argv) {
  const args = { kb: DEFAULT_KB_NAME };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--file') args.file = argv[i + 1];
    if (argv[i] === '--kb') args.kb = argv[i + 1];
  }
  return args;
}

function runNode(script, scriptArgs) {
  const r = spawnSync(process.execPath, [script, ...scriptArgs], { encoding: 'utf8' });
  if (r.error) throw new Error(`${path.basename(script)} 启动失败: ${r.error.message}`);
  if (r.status !== 0) {
    throw new Error(`${path.basename(script)} 执行失败: ${(r.stderr || r.stdout || '').trim()}`);
  }
  return (r.stdout || '').trim();
}

function parseJsonSafe(text, label) {
  try {
    const parsed = JSON.parse(text);
    if (parsed && parsed.code !== undefined && parsed.code !== 0) {
      throw new Error(`${label} 接口返回 code=${parsed.code}: ${parsed.msg || '无 msg'}`);
    }
    return parsed;
  } catch (e) {
    if (e instanceof Error && /接口返回 code/.test(e.message)) throw e;
    throw new Error(`${label} 响应解析失败: ${text.slice(0, 300)}`);
  }
}

async function resolveKbId(imaApi, kbName) {
  let cursor = '';
  for (let page = 0; page < 5; page += 1) {
    const resp = parseJsonSafe(
      await imaApi('openapi/wiki/v1/search_knowledge_base', { query: kbName, cursor, limit: 20 }),
      'search_knowledge_base'
    );
    const list = (resp.data && resp.data.info_list) || [];
    const hit = list.find((x) => x.kb_name === kbName);
    if (hit) return hit.kb_id;
    if (resp.data && resp.data.is_end) break;
    cursor = (resp.data && resp.data.next_cursor) || '';
    if (!cursor) break;
  }
  fail(`未找到知识库「${kbName}」，请确认名称或先在 ima 中创建。`);
}

function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.file) fail('缺少 --file 参数。');
  if (!fs.existsSync(args.file)) fail(`文件不存在: ${args.file}`);

  for (const p of [IMA_API, PREFLIGHT, COS_UPLOAD]) {
    if (!fs.existsSync(p)) fail(`依赖缺失: ${p}`);
  }

  const { imaApi } = require(IMA_API);

  // ── GATE 1: 类型检查 ──
  const pre = JSON.parse(runNode(PREFLIGHT, ['--file', args.file]));
  if (!pre || pre.pass === false) fail(`文件类型不受支持: ${(pre && pre.reason) || '未知原因'}`);

  const { file_name: fileName, file_ext: fileExt, file_size: fileSize, media_type: mediaType, content_type: contentType } = pre;

  // ── 定位知识库 ──
  const kbId = await resolveKbId(imaApi, args.kb);

  // ── GATE 3: 重名检查 ──
  let finalName = fileName;
  const repResp = parseJsonSafe(
    await imaApi('openapi/wiki/v1/check_repeated_names', {
      params: [{ name: fileName, media_type: mediaType }],
      knowledge_base_id: kbId,
    }),
    'check_repeated_names'
  );
  const rep = ((repResp.data && repResp.data.results) || [])[0];
  if (rep && rep.is_repeated) {
    const dot = fileName.lastIndexOf('.');
    const base = dot > 0 ? fileName.slice(0, dot) : fileName;
    const ext = dot > 0 ? fileName.slice(dot + 1) : '';
    finalName = ext ? `${base}_${stamp()}.${ext}` : `${base}_${stamp()}`;
  }

  // ── Step 4: create_media ──
  const createResp = parseJsonSafe(
    await imaApi('openapi/wiki/v1/create_media', {
      file_name: finalName,
      file_size: fileSize,
      content_type: contentType,
      knowledge_base_id: kbId,
      file_ext: fileExt,
    }),
    'create_media'
  );
  const mediaId = createResp.data && createResp.data.media_id;
  const cos = createResp.data && createResp.data.cos_credential;
  if (!mediaId || !cos) fail('create_media 未返回 media_id 或 COS 凭证。');

  // ── GATE 4: COS 上传 ──
  runNode(COS_UPLOAD, [
    '--file', args.file,
    '--secret-id', cos.secret_id,
    '--secret-key', cos.secret_key,
    '--token', cos.token,
    '--bucket', cos.bucket_name,
    '--region', cos.region,
    '--cos-key', cos.cos_key,
    '--content-type', contentType,
    '--start-time', String(cos.start_time),
    '--expired-time', String(cos.expired_time),
    '--timeout', '300000',
  ]);

  // ── GATE 2: add_knowledge（title 必须等于 file_name）──
  parseJsonSafe(
    await imaApi('openapi/wiki/v1/add_knowledge', {
      media_type: mediaType,
      media_id: mediaId,
      title: finalName,
      knowledge_base_id: kbId,
      file_info: { cos_key: cos.cos_key, file_size: fileSize, file_name: finalName },
    }),
    'add_knowledge'
  );

  process.stdout.write(
    JSON.stringify({ ok: true, title: finalName, kb_name: args.kb, media_id: mediaId, message: `已同步到 ima 知识库「${args.kb}」` }) + '\n'
  );
}

main().catch((e) => fail((e && e.message) || String(e)));
