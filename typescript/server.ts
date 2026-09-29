console.log("Hello world")
import { type BunRequest } from "bun";


const handleChatEndpoint = (req: BunRequest) => {
    let headers = req.headers;

    console.log("new request from ", headers.toJSON().host)

    return new Response("<h1>hello</h1>", {
        headers: { "Content-Type": "text/html" },
    })
}

const server = Bun.serve({
    routes: {
        "/": handleChatEndpoint,
        "/chat": handleChatEndpoint
    }
})

console.log("Server running at http://localhost:3000");

