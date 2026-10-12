# Rate relay (Cloudflare Worker)

1. dash.cloudflare.com me free account banao -> Workers & Pages -> Create -> Create Worker (Hello World) -> naam do (jaise `ss-rates`) -> Deploy.
2. "Edit code" kholo, sab kuch hata ke `worker.js` ka poora code paste karo -> Deploy.
3. Worker ka link (https://ss-rates.<tumhara-naam>.workers.dev) browser me kholo. Rates ka text dikhna chahiye. "upstream unavailable" aaye to neeche dekho.
4. Link Claude ko do. Wo `config.json` me `"feedUrl": "<link>"` daal dega. Sabke phone me bina update ke relay se rates aane lagenge.

Free plan: 100,000 requests/din. App har 3 sec me poochti hai, isliye ~1000 customers jo roz ~5 min app kholte hain, tak free me chalega.
Zyada ho to Workers Paid ($5/mahina) lo.

Dhyan: original feed ka port 7768 hai. Cloudflare Workers shayad non-standard port par connect na kare. Aisa ho to "upstream unavailable" aayega;
tab Deno Deploy / Render jaise host par yahi code chalana padega (worker.js me bas fetch ka URL wahi rahega).
