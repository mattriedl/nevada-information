// Front door for nevadainformation.com: one canonical URL per page, then the static site from public/.
const CANONICAL = 'nevadainformation.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const target = new URL(url);

    // www.nevadainformation.com and plain http -> https://nevadainformation.com.
    if (url.hostname === 'www.' + CANONICAL || (url.hostname === CANONICAL && url.protocol === 'http:')) {
      target.hostname = CANONICAL;
      target.protocol = 'https:';
    }
    // Folder URLs: /cities/reno and /cities/reno/index.html -> /cities/reno/
    // (the static asset server would otherwise answer these with a temporary 307).
    const last = url.pathname.split('/').pop();
    if (last === 'index.html') target.pathname = url.pathname.slice(0, -'index.html'.length);
    else if (last && !last.includes('.')) target.pathname = url.pathname + '/';

    // Everything above in one permanent hop.
    if (target.href !== url.href) return Response.redirect(target.toString(), 301);

    const response = await env.ASSETS.fetch(request);

    // The workers.dev address stays usable as a preview but must not compete with the real domain in search.
    if (url.hostname.endsWith('.workers.dev')) {
      const r = new Response(response.body, response);
      r.headers.set('X-Robots-Tag', 'noindex, nofollow');
      return r;
    }
    return response;
  },
};
