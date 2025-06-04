"use client";

import { io } from "socket.io-client";

export const websocket = io(process.env.NEXT_PUBLIC_SOCKET_URL, {
	transports: ["websocket"],
});

export function connectSocket() {
	if (websocket.connected) {
		return websocket;
	}

	websocket.connect();

	websocket.on("connect", () => {
		console.log("Socket connected");
	});

	websocket.on("disconnect", () => {
		console.log("Socket disconnected");
	});
}
