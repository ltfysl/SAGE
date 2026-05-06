export async function analyzeLog(formData: FormData) {
  const file = formData.get("file");
  return { status: "ok", fileName: (file as File).name };
}
