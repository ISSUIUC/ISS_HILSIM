import { useWebsocket } from "../websocket";

export default function WebsocketStatus() {
    let online = useWebsocket()
    return <h2>Websocket connected: {JSON.stringify(online)}</h2>;
}