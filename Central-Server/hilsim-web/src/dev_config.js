const server_url_request = await fetch("https://raw.githubusercontent.com/ISSUIUC/ISS_HILSIM/active_server_url/server_url.txt");

const text = await server_url_request.text();

console.log(text);

export const api_url = text;
// /api/jobs/list