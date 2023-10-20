import React from "react";
import { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";

function Main() {
    const [val, updateVal] = useState("bad");
    
    const location = useLocation();

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }

    async function GetCookie() {
        // await sleep(5000)
        // updateVal("p")
        const location = useLocation();
        const queryParams = new URLSearchParams(location.search);
        const code = queryParams.get("code")
      
        try {
        //     const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
        //     const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
      
        //   const data = await fetch('https://jsonplaceholder.typicode.com/posts', {
        //         method: "POST",
        //   }).then((response) => response.json());

            //https://github.com/login/oauth/authorize?client_id=70662875937be8f7bce6&client_secret=89c565b3761740ca3710c3c31d41c1859fa3ab95&code=
            // const githubOAuthURL = `https://github.com/login/oauth/authorize?client_id=${process.env.REACT_APP_GITHUB_CLIENT_ID}&client_secret=${process.env.REACT_APP_GITHUB_CLIENT_SECRET}&code=${code}`;
            // const githubOAuthURL = `https://github.com/login/oauth/access_token?client_id=${process.env.REACT_APP_GITHUB_CLIENT_ID}&client_secret=89c565b3761740ca3710c3c31d41c1859fa3ab95&code=${code}`;
            const githubOAuthURL = 'https://github.com/login/oauth/access_token'
            // const data = await fetch(githubOAuthURL, {
            //     method: "POST",
            //     headers: {
            //             'Content-Type': 'application/json'
            //     }
            // }).then((response) => response.json());

            // const data = await fetch(githubOAuthURL, {
            //     method: "POST",
            //     body: "{client_id:process.env.REACT_APP_GITHUB_CLIENT_ID, client_secret89c565b3761740ca3710c3c31d41c1859fa3ab95:}"
            //     body: "{client_id:process.env.REACT_APP_GITHUB_CLIENT_ID, client_secret:, code:}"
            //     headers: {
            //             'Content-Type': 'application/json'
            //     }
            // }).then((response) => response.json());

            const data = await fetch(githubOAuthURL, {
                mode: 'no-cors',
                method: "POST",
                body: {
                    client_id: process.env.REACT_APP_GITHUB_CLIENT_ID,
                    client_secret: '',
                    code: 'e849b80e0ab4914d1671'
                },
                headers: {
                        'Content-Type': 'application/json',
                        // 'Access-Control-Allow-Origin':'http://localhost/'
                }
            }).then((response) => response.json())

            // const accessToken = data.access_token;
            console.log(data.id)

            sessionStorage.setItem("idv", data.id)

            // const accessToken = 'ppe';
            updateVal(data)
      
        } catch (error) {
          console.error(error)
          updateVal("error")
          sessionStorage.setItem("idv", error)
        }
      }
    
    if (val=="bad") {
        updateVal(() => (GetCookie()))    
    }

    const queryParams = new URLSearchParams(location.search);
    return <div>
                <h2>This will be the homepage! {queryParams.get("code")}</h2>
                <p>{sessionStorage.getItem("idv")}</p>
            </div>
}

export default Main;