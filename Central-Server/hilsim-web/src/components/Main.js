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
            const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
            const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
      
          const data = await fetch('https://jsonplaceholder.typicode.com/posts', {
                method: "POST",
          }).then((response) => response.json());

        //   const data = await fetch('https://github.com/login/oauth/access_token', {
        //         method: "POST",
        //         body: {
        //                 client_id: GITHUB_CLIENT_ID,
        //                 client_secret: GITHUB_CLIENT_SECRET,
        //                 code: code,
        //         },
        //         headers: {
        //                 'Content-Type': 'application/json'
        //         }
        //     }).then((response) => response.json());
            // const accessToken = data.access_token;
            console.log(data.id)

            sessionStorage.setItem("idv", data.id)

            const accessToken = 'ppe';
            updateVal(data)
      
        } catch (error) {
          console.error(error);
          updateVal("error")
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