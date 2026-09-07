import { cleanRawSvg } from '../svgParser';

export function generateMinifiedSvg(parsed) {
  const cleaned = cleanRawSvg(parsed.cleanedSvg || parsed.raw);

  // Strip linebreaks and collapse whitespace
  return cleaned
    .replace(/>\s+</g, '><')
    .trim();
}
