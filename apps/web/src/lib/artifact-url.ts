export function artifactUrl(path: string | null | undefined): string | undefined {
  if (!path) return undefined;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  if (path.startsWith("/artifact?")) return path;
  return `/artifact?path=${encodeURIComponent(path)}`;
}
