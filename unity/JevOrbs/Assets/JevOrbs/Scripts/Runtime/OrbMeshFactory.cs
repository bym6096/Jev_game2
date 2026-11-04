using System.Collections.Generic;
using UnityEngine;

namespace JevOrbs
{
    /// <summary>Flat-shaded low-poly sphere (faceted icosphere) with per-name vertex wobble, so every bead is a slightly different gem.</summary>
    public static class OrbMeshFactory
    {
        static float Hash01(int seed, int i)
        {
            unchecked
            {
                uint h = (uint)seed * 2654435761u ^ (uint)(i + 1) * 40503u;
                h ^= h >> 13; h *= 1274126177u; h ^= h >> 16;
                return (h & 0xFFFFFF) / (float)0x1000000;
            }
        }

        public static int SeedOf(string s)
        {
            unchecked { int h = 17; foreach (char c in s ?? "") h = h * 31 + c; return h; }
        }

        struct Tri { public int a, b, c; }

        static void Icosphere(int subdiv, out List<Vector3> verts, out List<Tri> tris)
        {
            float t = (1f + Mathf.Sqrt(5f)) / 2f;
            verts = new List<Vector3>
            {
                new Vector3(-1, t, 0), new Vector3(1, t, 0), new Vector3(-1, -t, 0), new Vector3(1, -t, 0),
                new Vector3(0, -1, t), new Vector3(0, 1, t), new Vector3(0, -1, -t), new Vector3(0, 1, -t),
                new Vector3(t, 0, -1), new Vector3(t, 0, 1), new Vector3(-t, 0, -1), new Vector3(-t, 0, 1)
            };
            for (int i = 0; i < verts.Count; i++) verts[i] = verts[i].normalized;
            int[] f =
            {
                0,11,5, 0,5,1, 0,1,7, 0,7,10, 0,10,11, 1,5,9, 5,11,4, 11,10,2, 10,7,6, 7,1,8,
                3,9,4, 3,4,2, 3,2,6, 3,6,8, 3,8,9, 4,9,5, 2,4,11, 6,2,10, 8,6,7, 9,8,1
            };
            tris = new List<Tri>();
            for (int i = 0; i < f.Length; i += 3) tris.Add(new Tri { a = f[i], b = f[i + 1], c = f[i + 2] });
            for (int s = 0; s < subdiv; s++)
            {
                var cache = new Dictionary<long, int>();
                var next = new List<Tri>();
                foreach (var tr in tris)
                {
                    int ab = Mid(verts, cache, tr.a, tr.b), bc = Mid(verts, cache, tr.b, tr.c), ca = Mid(verts, cache, tr.c, tr.a);
                    next.Add(new Tri { a = tr.a, b = ab, c = ca }); next.Add(new Tri { a = tr.b, b = bc, c = ab });
                    next.Add(new Tri { a = tr.c, b = ca, c = bc }); next.Add(new Tri { a = ab, b = bc, c = ca });
                }
                tris = next;
            }
        }

        static int Mid(List<Vector3> verts, Dictionary<long, int> cache, int a, int b)
        {
            long key = a < b ? ((long)a << 32) | (uint)b : ((long)b << 32) | (uint)a;
            int idx;
            if (cache.TryGetValue(key, out idx)) return idx;
            verts.Add(((verts[a] + verts[b]) * 0.5f).normalized);
            idx = verts.Count - 1; cache[key] = idx;
            return idx;
        }

        /// <summary>A unit-diameter faceted sphere. jitter: how much each vertex may move in or out (0.03 smooth gem .. 0.09 rough stone).
        /// crack: split along a jagged plane and push the halves apart (a shattered bead).</summary>
        public static Mesh Build(string name, int subdiv, float jitter, bool crack)
        {
            int seed = SeedOf(name);
            List<Vector3> v; List<Tri> tris;
            Icosphere(subdiv, out v, out tris);
            var dirs = new List<Vector3>(v);                         // unit directions (for UVs)
            for (int i = 0; i < v.Count; i++) v[i] = v[i] * (0.5f * (1f + (Hash01(seed, i) - 0.5f) * 2f * jitter));

            Vector3 crackN = new Vector3(Hash01(seed, 901) - 0.5f, Hash01(seed, 902) * 0.6f + 0.2f, Hash01(seed, 903) - 0.5f).normalized;
            float crackD = (Hash01(seed, 904) - 0.5f) * 0.12f;

            var verts = new List<Vector3>(tris.Count * 3);
            var uvs = new List<Vector2>(tris.Count * 3);
            var idx = new List<int>(tris.Count * 3);
            foreach (var t in tris)
            {
                Vector3 pa = v[t.a], pb = v[t.b], pc = v[t.c];
                Vector3 centroid = (pa + pb + pc) / 3f;
                Vector3 n = Vector3.Cross(pb - pa, pc - pa);
                bool flip = Vector3.Dot(n, centroid) < 0f;            // make sure the face looks outward
                if (flip) { Vector3 tmp = pb; pb = pc; pc = tmp; }
                int ia = t.a, ib = flip ? t.c : t.b, ic = flip ? t.b : t.c;
                if (crack)
                {
                    float side = Vector3.Dot(centroid, crackN) - crackD > 0f ? 1f : -1f;
                    Vector3 shift = crackN * (0.035f * side);
                    pa += shift; pb += shift; pc += shift;
                }
                int baseIdx = verts.Count;
                verts.Add(pa); verts.Add(pb); verts.Add(pc);
                float ua = U(dirs[ia]), ub = U(dirs[ib]), uc = U(dirs[ic]);
                float mx = Mathf.Max(ua, Mathf.Max(ub, uc)), mn = Mathf.Min(ua, Mathf.Min(ub, uc));
                if (mx - mn > 0.5f) { if (ua < 0.5f) ua += 1f; if (ub < 0.5f) ub += 1f; if (uc < 0.5f) uc += 1f; }   // triangle across the texture seam
                uvs.Add(new Vector2(ua, V(dirs[ia]))); uvs.Add(new Vector2(ub, V(dirs[ib]))); uvs.Add(new Vector2(uc, V(dirs[ic])));
                idx.Add(baseIdx); idx.Add(baseIdx + 1); idx.Add(baseIdx + 2);
            }
            var mesh = new Mesh { name = "JevOrb_" + name };
            mesh.SetVertices(verts); mesh.SetUVs(0, uvs); mesh.SetTriangles(idx, 0);
            mesh.RecalculateNormals();                                // vertices are not shared, so every face keeps its own normal: flat shading
            mesh.RecalculateBounds();
            return mesh;
        }

        static float U(Vector3 d) { return Mathf.Atan2(d.z, d.x) / (2f * Mathf.PI) + 0.5f; }
        static float V(Vector3 d) { return Mathf.Asin(Mathf.Clamp(d.y, -1f, 1f)) / Mathf.PI + 0.5f; }

        /// <summary>A flat ring (low-poly torus) for the gold band of a gold-leaf blank.</summary>
        public static Mesh Torus(float majorR, float minorR, int seg, int sides)
        {
            var verts = new List<Vector3>(); var idx = new List<int>();
            for (int i = 0; i < seg; i++)
                for (int j = 0; j < sides; j++)
                {
                    Vector3 P(int ii, int jj)
                    {
                        float a = (ii % seg) / (float)seg * Mathf.PI * 2f, b = (jj % sides) / (float)sides * Mathf.PI * 2f;
                        float r = majorR + minorR * Mathf.Cos(b);
                        return new Vector3(r * Mathf.Cos(a), minorR * Mathf.Sin(b), r * Mathf.Sin(a));
                    }
                    Vector3 p00 = P(i, j), p10 = P(i + 1, j), p01 = P(i, j + 1), p11 = P(i + 1, j + 1);
                    int s = verts.Count;
                    verts.AddRange(new[] { p00, p11, p10, p00, p01, p11 });   // clockwise seen from outside (Unity front face)
                    for (int k = 0; k < 6; k++) idx.Add(s + k);
                }
            var m = new Mesh { name = "JevTorus" };
            m.SetVertices(verts); m.SetTriangles(idx, 0); m.RecalculateNormals(); m.RecalculateBounds();
            return m;
        }

        /// <summary>A flat-shaded n-sided prism (radius 0.5, height 1, centered): pedestals and tabletops.</summary>
        public static Mesh Prism(int sides)
        {
            var verts = new List<Vector3>(); var idx = new List<int>();
            Vector3 P(int i, float y) { float a = i / (float)sides * Mathf.PI * 2f; return new Vector3(Mathf.Cos(a) * 0.5f, y, Mathf.Sin(a) * 0.5f); }
            for (int i = 0; i < sides; i++)
            {
                Vector3 b0 = P(i, -0.5f), b1 = P(i + 1, -0.5f), t0 = P(i, 0.5f), t1 = P(i + 1, 0.5f);
                int s = verts.Count;
                verts.AddRange(new[] { b0, t1, b1, b0, t0, t1 });                                   // side, seen from outside
                verts.AddRange(new[] { new Vector3(0, 0.5f, 0), t1, t0 });                           // top cap
                verts.AddRange(new[] { new Vector3(0, -0.5f, 0), b0, b1 });                          // bottom cap
                for (int k = 0; k < 12; k++) idx.Add(s + k);
            }
            var m = new Mesh { name = "JevPrism" };
            m.SetVertices(verts); m.SetTriangles(idx, 0); m.RecalculateNormals(); m.RecalculateBounds();
            return m;
        }

        /// <summary>Small octahedron (shard) used for the accent bits that circle the stage bead.</summary>
        public static Mesh Shard()
        {
            Vector3[] p = { new Vector3(0, 1, 0), new Vector3(0, -1, 0), new Vector3(1, 0, 0), new Vector3(-1, 0, 0), new Vector3(0, 0, 1), new Vector3(0, 0, -1) };
            int[][] f = { new[] { 0, 4, 2 }, new[] { 0, 3, 4 }, new[] { 0, 5, 3 }, new[] { 0, 2, 5 }, new[] { 1, 2, 4 }, new[] { 1, 4, 3 }, new[] { 1, 3, 5 }, new[] { 1, 5, 2 } };
            var verts = new List<Vector3>(); var idx = new List<int>();
            foreach (var tri in f) { foreach (int k in tri) { idx.Add(verts.Count); verts.Add(p[k] * new Vector3(0.5f, 0.9f, 0.5f)); } }
            var m = new Mesh { name = "JevShard" };
            m.SetVertices(verts); m.SetTriangles(idx, 0); m.RecalculateNormals(); m.RecalculateBounds();
            return m;
        }
    }
}
