// Copy index-student.html to index.html for build
const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'index-student.html');
const dest = path.join(__dirname, 'index.html');

fs.copyFileSync(source, dest);
console.log('✓ Copied index-student.html to index.html');
