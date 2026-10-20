const ResEdit = require('resedit'); const fs = require('fs');
const [,, inp, ico, out] = process.argv;
const exe = ResEdit.NtExecutable.from(fs.readFileSync(inp));
const res = ResEdit.NtExecutableResource.from(exe);
const icon = ResEdit.Data.IconFile.from(fs.readFileSync(ico));
ResEdit.Resource.IconGroupEntry.replaceIconsForResource(res.entries, 1, 1033, icon.icons.map(i => i.data));
const vi = ResEdit.Resource.VersionInfo.createEmpty();
vi.setFileVersion(1, 0, 0, 0, 1033); vi.setProductVersion(1, 0, 0, 0, 1033);
vi.setStringValues({ lang: 1033, codepage: 1200 }, {
  FileDescription: 'Shree SS Jewellers Rate Board', ProductName: 'Shree SS Rate Board', CompanyName: 'Shree SS Jewellers',
  FileVersion: '1.0.0.0', ProductVersion: '1.0.0.0', OriginalFilename: 'SSRateBoard.exe', InternalName: 'SSRateBoard',
  LegalCopyright: 'Shree SS Jewellers, Jaora' });
vi.outputToResourceEntries(res.entries);
res.outputResource(exe);
fs.writeFileSync(out, Buffer.from(exe.generate()));
console.log('ok', fs.statSync(out).size);
