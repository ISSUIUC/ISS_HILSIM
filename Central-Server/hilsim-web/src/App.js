import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import { socket, useWebsocket } from './websocket';

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Page404 from './components/Page404';
import WebsocketStatus from './components/WebsocketStatus';
import HomePage from './components/homepage';

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "*",
    element: <div><Page404 /></div>,
  },
  {
    path: "/wsstatus",
    element: <WebsocketStatus />,
  },
]);


function App() {
  return (
    <div className="App">
      <RouterProvider router={router} />
    </div>
  );
}

export default App;
