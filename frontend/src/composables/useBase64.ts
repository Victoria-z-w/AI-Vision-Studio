/**
 * Composable for handling base64 images: download, display helpers.
 */
export function useBase64() {
  /** Convert a base64 data URI to a Blob for download. */
  function base64ToBlob(base64: string): Blob {
    const [header, data] = base64.split(",");
    const mime = header.match(/data:(.*?);/)?.[1] || "image/png";
    const bytes = atob(data);
    const buf = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) {
      buf[i] = bytes.charCodeAt(i);
    }
    return new Blob([buf], { type: mime });
  }

  /** Download a base64 data URI as a file. */
  function downloadBase64(base64: string, filename: string) {
    const blob = base64ToBlob(base64);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /** Check if a string is a valid base64 data URI. */
  function isBase64DataUri(value: unknown): value is string {
    return typeof value === "string" && value.startsWith("data:image/");
  }

  return { base64ToBlob, downloadBase64, isBase64DataUri };
}
