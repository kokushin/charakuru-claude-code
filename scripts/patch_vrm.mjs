// node patch_vrm.mjs <in.vrm> <out.vrm> --meta-from <app_exported.vrm>
// Rewrites only the glTF JSON chunk of a VRM 1.0 file, copying VRMC_vrm.meta (model name, authors, license) from
// the VRM the Charakuru app exported. The app writes that metadata straight into its VRM, so a VRM exported from
// avatar.blend (e.g. by make_vrm_expressions.py) would otherwise carry "undefined". thumbnailImage is an image
// index of the source file, so the target keeps its own. <out.vrm> may equal <in.vrm>; it is replaced atomically.
import fs from 'node:fs'

const [input, output, ...rest] = process.argv.slice(2)
const i = rest.indexOf('--meta-from')
if (!input || !output || i < 0 || !rest[i + 1]) {
  console.error('usage: node patch_vrm.mjs <in.vrm> <out.vrm> --meta-from <app_exported.vrm>')
  process.exit(1)
}
const readGlb = (file) => {
  const b = fs.readFileSync(file)
  if (b.toString('ascii', 0, 4) !== 'glTF' || b.toString('ascii', 16, 20) !== 'JSON') throw new Error('not a binary glTF / VRM: ' + file)
  const jsonLength = b.readUInt32LE(12)
  const json = JSON.parse(b.subarray(20, 20 + jsonLength).toString('utf8'))
  if (!json.extensions?.VRMC_vrm?.meta) throw new Error('not a VRM 1.0 file (no VRMC_vrm.meta): ' + file)
  return { json, tail: b.subarray(20 + jsonLength) }
}
const { json, tail } = readGlb(input)
const target = json.extensions.VRMC_vrm
const meta = { ...readGlb(rest[i + 1]).json.extensions.VRMC_vrm.meta }
delete meta.thumbnailImage
if (target.meta.thumbnailImage !== undefined) meta.thumbnailImage = target.meta.thumbnailImage
target.meta = meta
let text = JSON.stringify(json)
while (Buffer.byteLength(text) % 4) text += ' '
const jsonBytes = Buffer.from(text, 'utf8')
const header = Buffer.alloc(20)
header.write('glTF', 0, 'ascii'); header.writeUInt32LE(2, 4)
header.writeUInt32LE(20 + jsonBytes.length + tail.length, 8)
header.writeUInt32LE(jsonBytes.length, 12); header.write('JSON', 16, 'ascii')
const temp = output + '.tmp'
fs.writeFileSync(temp, Buffer.concat([header, jsonBytes, tail]))
fs.renameSync(temp, output)
console.log('patched meta', output, meta.name)
