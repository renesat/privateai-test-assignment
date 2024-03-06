export async function getPapersList() {
  const response = await fetch(import.meta.env.VITE_API_URL + "/paper", {
    method: "GET",
  });
  return await response.json();
}

export async function getPaperInfo(paperId) {
  const response = await fetch(
    import.meta.env.VITE_API_URL + "/paper/" + paperId,
    {
      method: "GET",
    },
  );
  return await response.json();
}

export async function uploadPaper(file) {
  let formData = new FormData();
  formData.append("file", file);
  const response = await fetch(import.meta.env.VITE_API_URL + "/paper", {
    method: "POST",
    body: formData,
  });
  return await response.json();
}
