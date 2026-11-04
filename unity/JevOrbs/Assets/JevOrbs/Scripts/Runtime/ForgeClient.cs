using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;

namespace JevOrbs
{
    public class ForgeResult<T> where T : class
    {
        public T value;
        public string error;
        public bool offline;    // no server there (not running, wrong address, or no network): the game falls back to the sample beads
        public bool needCode;   // the server wants ACCESS_CODE
    }

    /// <summary>
    /// Talks to the same thin server as the web toy (toys/card-forge/server.py locally, api/forge.py + api/hero.py on Vercel).
    /// The Jev key stays on the server; a shipped game must never contain it.
    /// </summary>
    public class ForgeClient
    {
        public string baseUrl = "http://localhost:8000";
        public string accessCode = "";
        public int timeoutSeconds = 30;

        static Task<UnityWebRequest> Send(UnityWebRequest req)
        {
            var tcs = new TaskCompletionSource<UnityWebRequest>();
            var op = req.SendWebRequest();
            op.completed += _ => tcs.TrySetResult(req);
            return tcs.Task;
        }

        class ErrorBody { public string error; public bool need_code; }

        async Task<ForgeResult<T>> Post<T>(string path, object body, Func<string, T> parse) where T : class
        {
            var res = new ForgeResult<T>();
            var url = (baseUrl ?? "").TrimEnd('/') + path;
            var bytes = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(body));
            using (var req = new UnityWebRequest(url, "POST"))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                req.timeout = timeoutSeconds;
                await Send(req);
                long code = req.responseCode;
                string text = req.downloadHandler != null ? req.downloadHandler.text : "";
                if (req.result == UnityWebRequest.Result.ConnectionError || code == 0 || code == 404 || code == 405) { res.offline = true; res.error = "서버에 연결할 수 없습니다"; return res; }
                if (code == 200)
                {
                    try { res.value = parse(text); }
                    catch (Exception) { res.value = null; }
                    if (res.value == null) res.error = "서버 응답을 읽을 수 없습니다";
                    return res;
                }
                ErrorBody eb = null;
                try { eb = JsonConvert.DeserializeObject<ErrorBody>(text); } catch (Exception) { }
                res.needCode = code == 403;
                res.error = eb != null && !string.IsNullOrEmpty(eb.error) ? eb.error : "오류 " + code;
                return res;
            }
        }

        public Task<ForgeResult<Card>> ForgeAsync(string name, string lang)
        {
            return Post<Card>("/forge", new { name, lang, code = accessCode ?? "" }, t => CardRules.Clean(JsonConvert.DeserializeObject<Card>(t)));
        }

        public Task<ForgeResult<Hero>> HeroAsync(List<string> names, string lang)
        {
            return Post<Hero>("/hero", new { names, lang, code = accessCode ?? "" }, t => CardRules.CleanHero(JsonConvert.DeserializeObject<Hero>(t)));
        }
    }
}
