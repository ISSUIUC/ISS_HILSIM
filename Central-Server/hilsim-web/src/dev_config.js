const server_url_request = await fetch("https://raw.githubusercontent.com/ISSUIUC/ISS_HILSIM/active_server_url/server_url.txt");

const text = await server_url_request.text();

await fetch(text).then(response => {
    console.log("Fetched URL is valid.")
}).catch(error => {
    console.log("Fetched URL was not valid.")
    console.log("Valid URL check failed with error: " + error.message)
    console.log("Setting API URL to localhost")

    text = "http://localhost"
});

console.log(text);

// test url

export const api_url = text.trim();
// /api/jobs/list