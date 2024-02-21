import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import { socket, useWebsocket } from './websocket';

import {
  createBrowserRouter,
  RouterProvider,
  Routes,
  Route
} from "react-router-dom";
import Page404 from './pages/Page404';
import WebsocketStatus from './pages/WebsocketStatus';
import Queue from './pages/queue';
import HomePage from './pages/homepage';
import New_Job from './pages/newjob';
import SwaggerUIPage from './pages/swagger';
import Jobs from './pages/jobs';
import TestingDashboard from './pages/testingdashboard';

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/new_job",
    element: <New_Job />,
  },
  {
    path: "/testing_dash",
    element: <TestingDashboard />,
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
    path: "/docs",
    element: <SwaggerUIPage />,
  },
  {
    path: "/jobs",
    element: <Jobs />,
  }
]);


function App() {
  return (
    <div className="App">
      <RouterProvider router={router}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new_job" element={<New_Job />}/>
        </Routes>
      </RouterProvider>
      
    </div>
  );
}

export default App;
