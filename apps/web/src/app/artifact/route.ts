import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

const MIME_TYPES: Record<string, string> = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".json": "application/json",
  ".png": "image/png",
  ".txt": "text/plain; charset=utf-8",
};

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const ALLOWED_ROOTS = [
  `${REPO_ROOT}/data`,
  `${REPO_ROOT}/demo`,
  `${REPO_ROOT}/runs`,
];

function isInside(parent: string, child: string) {
  const relative = path.relative(parent, child);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const requestedPath = url.searchParams.get("path");
  if (!requestedPath) {
    return NextResponse.json({ error: "missing path" }, { status: 400 });
  }

  const target = path.resolve(
    path.isAbsolute(requestedPath)
      ? requestedPath
      : path.join(/* turbopackIgnore: true */ REPO_ROOT, requestedPath),
  );

  if (!ALLOWED_ROOTS.some((allowed) => isInside(allowed, target))) {
    return NextResponse.json({ error: "artifact path is not allowed" }, { status: 403 });
  }

  try {
    const file = await readFile(target);
    const contentType =
      MIME_TYPES[path.extname(target).toLowerCase()] ?? "application/octet-stream";
    return new Response(file, {
      headers: {
        "Cache-Control": "no-store",
        "Content-Type": contentType,
      },
    });
  } catch {
    return NextResponse.json({ error: "artifact not found" }, { status: 404 });
  }
}
