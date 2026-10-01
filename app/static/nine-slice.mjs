// Paint all nine regions onto one surface with shared device-pixel boundaries.
export function renderNineSlice(image, c, width, height, ratio = 1) {
  const canvas = document.createElement('canvas');
  canvas.width = Math.max(1, Math.round(width * ratio));
  canvas.height = Math.max(1, Math.round(height * ratio));
  const context = canvas.getContext('2d');
  const sx = [0, c.left, c.right, c.width];
  const sy = [0, c.top, c.bottom, c.height];
  function edges(total, first, last) {
    const fit = Math.min(1, total / ((first + last) * c.scale * ratio));
    return [0, Math.round(first * c.scale * ratio * fit), total - Math.round(last * c.scale * ratio * fit), total];
  }
  const dx = edges(canvas.width, c.left, c.width - c.right);
  const dy = edges(canvas.height, c.top, c.height - c.bottom);
  for (let y = 0; y < 3; y++) for (let x = 0; x < 3; x++) {
    const w = dx[x + 1] - dx[x], h = dy[y + 1] - dy[y];
    if (w > 0 && h > 0) context.drawImage(image, sx[x], sy[y], sx[x + 1] - sx[x], sy[y + 1] - sy[y], dx[x], dy[y], w, h);
  }
  return canvas.toDataURL('image/png');
}
