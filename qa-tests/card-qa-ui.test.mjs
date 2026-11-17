import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readFileSync} from 'node:fs';
const page=readFileSync(new URL('../card-qa.html',import.meta.url),'utf8');
const library=readFileSync(new URL('../vendor/qrcode.min.js',import.meta.url),'utf8');
test('mobile QR page never persists personal tokens in web storage',()=>{
 assert.ok(!page.includes('localStorage'));
 assert.ok(!page.includes('sessionStorage'));
 assert.ok(!page.includes('document.cookie'));
 assert.ok(page.includes("referrerPolicy:'no-referrer'"));
 assert.ok(page.includes('generation++'));
});
test('QR is generated locally with pinned in-repo vendor library',()=>{
 assert.ok(page.includes('vendor/qrcode.min.js'));
 assert.ok(page.includes('new QRCode(shell,'));
 assert.ok(page.includes('QRCode.CorrectLevel.M'));
 assert.ok(library.length>10000);
 assert.ok(!page.includes('quickchart.io'));
 assert.ok(!page.includes('api.qrserver.com'));
});
test('QR UI requires same-origin verified identity for issue / read / revoke',()=>{
 assert.ok(page.includes('DFMP3AdminAuth'));
 assert.ok(page.includes('auth.isSignedIn()'));
 for(const endpoint of ['/api/card/me','/api/card/issue','/api/card/revoke'])assert.ok(page.includes(endpoint));
 assert.ok(page.includes("credentials:'same-origin'"));
 assert.ok(page.includes('reset()'));
});
