import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import { socket, useWebsocket } from './websocket';
import { createContext } from 'react';
import { useLocation } from "react-router-dom";

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Page404 from './components/Page404';
import WebsocketStatus from './components/WebsocketStatus';
import Login from './components/Login';

export const AuthContext = createContext();

async function SendCookie() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const code = queryParams.get("code")

  try {
    // Exchange the code for an access token
  const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
  const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;

    const data = await fetch('https://github.com/login/oauth/access_token', {
          method: "POST",
          body: {
                client_id: GITHUB_CLIENT_ID,
                client_secret: GITHUB_CLIENT_SECRET,
                code: code,
          },
          headers: {
                'Content-Type': 'application/json'
          }
    }).then((response) => response.json());

    const accessToken = data.access_token;
    return "AT: "+accessToken;

  } catch (error) {
    console.error(error);
    return "l";
  }
}

function RouteWithCookie() {
  const [val, updateVal] = useState("bad");

  const location = useLocation();
  // updateVal(SendCookie())
  const queryParams = new URLSearchParams(location.search);
  return <div>
            <h2>This will be the homepage! {queryParams.get("code")}</h2>
            <p>{val}</p>
        </div>
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <RouteWithCookie/>,
  },
  {
    path: "*",
    element: <div><Page404 /></div>,
  },
  {
    path: "/wsstatus",
    element: <WebsocketStatus />,
  },
  {
    path: "/login",
    element: <Login />
  }
]);


function App() {
  return (
    <div className="App">
      <RouterProvider router={router} />
    </div>
  );
}

export default App;
