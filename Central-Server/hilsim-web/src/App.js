import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import { socket, useWebsocket } from './websocket';
import { createContext } from 'react';

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Page404 from './components/Page404';
import WebsocketStatus from './components/WebsocketStatus';
import Login from './components/Login';

export const AuthContext = createContext();

const router = createBrowserRouter([
  {
    path: "/",
    element: <div><h2>This will be the homepage!</h2></div>,
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
