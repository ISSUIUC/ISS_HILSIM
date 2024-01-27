const server_url_request = await fetch("https://raw.githubusercontent.com/ISSUIUC/ISS_HILSIM/active_server_url/server_url.txt");

console.log(server_url_request)

export const api_url = server_url_request
// /api/jobs/list