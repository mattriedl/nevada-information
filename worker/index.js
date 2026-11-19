// Front door for nevadainformation.com: one canonical host, then the static site from public/.
const CANONICAL = 'nevadainformation.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // www.nevadainformation.com and plain http -> https://nevadainformation.com, same path, one hop.
    if (url.hostname === 'www.' + CANONICAL || (url.hostname === CANONICAL && url.protocol === 'http:')) {
      url.hostname = CANONICAL;
      url.protocol = 'https:';
      return Response.redirect(url.toString(), 301);
    }

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
