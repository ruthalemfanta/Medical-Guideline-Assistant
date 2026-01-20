// Simple script to help generate favicons
// You can run this with Node.js if you have the sharp library installed

const fs = require('fs');
const path = require('path');

// SVG content for the medical favicon
const svgContent = `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="6" fill="#2563eb"/>
  <rect x="13" y="8" width="6" height="16" fill="white" rx="1"/>
  <rect x="8" y="13" width="16" height="6" fill="white" rx="1"/>
  <circle cx="10" cy="10" r="1.5" fill="#93c5fd" opacity="0.8"/>
  <circle cx="22" cy="10" r="1.5" fill="#93c5fd" opacity="0.8"/>
  <circle cx="10" cy="22" r="1.5" fill="#93c5fd" opacity="0.8"/>
  <circle cx="22" cy="22" r="1.5" fill="#93c5fd" opacity="0.8"/>
</svg>`;

// Write the SVG file
fs.writeFileSync(path.join(__dirname, 'public', 'medical-favicon.svg'), svgContent);

console.log('✅ Medical favicon SVG created!');
console.log('📝 To convert to ICO format:');
console.log('   1. Visit https://favicon.io/favicon-converter/');
console.log('   2. Upload the medical-favicon.svg file');
console.log('   3. Download the generated favicon.ico');
console.log('   4. Replace public/favicon.ico with the new file');

// If you have sharp installed, uncomment this to generate PNG versions:
/*
const sharp = require('sharp');

async function generateFavicons() {
  const svgBuffer = Buffer.from(svgContent);
  
  // Generate different sizes
  const sizes = [16, 32, 48, 64, 128, 256];
  
  for (const size of sizes) {
    await sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(path.join(__dirname, 'public', `favicon-${size}x${size}.png`));
  }
  
  console.log('✅ PNG favicons generated!');
}

generateFavicons().catch(console.error);
*/