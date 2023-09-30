import { io } from 'socket.io-client';
import { useEffect, useState } from 'react';

// "undefined" means the URL will be computed from the `window.location` object
const URL = "http://localhost:443"



export function useWebsocket() {
    const socket = io(URL);
    const [isOnline, setIsOnline] = useState(false);

    useEffect(() => {
        const onConnect = () => {setIsOnline(true)}
        const onDisconnect = () => () => {setIsOnline(false)}
        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        return () => {
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
        };
    }, [setIsOnline]);
    return isOnline;
  }