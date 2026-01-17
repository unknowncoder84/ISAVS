// Copy index-teacher.html to index.html for build
const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'index-teacher.html');
const dest = path.join(__dirname, 'index.html');

fs.copyFileSync(source, dest);
console.log('✓ Copied index-teacher.html to index.html');
