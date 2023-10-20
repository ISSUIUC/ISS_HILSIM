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
        const location = useLocation();
        const queryParams = new URLSearchParams(location.search);
        const code = queryParams.get("code")
      
        fetch("http://localhost/api/authenticate", {
          method: "POST",
          body: JSON.stringify({
            github_code: code,
          }),
          headers: {
            "Content-type": "application/json"
          }
        }).then((res) => {
          updateVal(JSON.stringify(res))
        })

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