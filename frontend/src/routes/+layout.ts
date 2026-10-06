// SPA mode: render on the client only. This keeps the demo simple to deploy
// (e.g. Netlify Drop) and means the browser talks to the API directly.
// Flip `ssr` back to true later if you host the backend alongside the frontend.
export const ssr = false;
export const prerender = false;
