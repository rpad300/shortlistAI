# Criar Storage Buckets no Supabase

**AÇÃO OBRIGATÓRIA** para upload de ficheiros funcionar!

---

## 📝 Instruções (2 minutos)

### 1. Aceder ao Supabase Storage

https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/storage

### 2. Criar Bucket para CVs

1. Clica em "New bucket"
2. Nome: `cvs`
3. Public: **NO** (private)
4. File size limit: 10 MB
5. Allowed MIME types: `application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document`
6. Clica "Create bucket"

### 3. Criar Bucket para Job Postings

1. Clica em "New bucket" novamente
2. Nome: `job-postings`
3. Public: **NO** (private)
4. File size limit: 10 MB
5. Allowed MIME types: `application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document`
6. Clica "Create bucket"

### 4. Configurar RLS Policies (Opcional)

Para cada bucket, adicionar policies:

```sql
-- Policy para service role pode fazer tudo
CREATE POLICY "Service role can do everything"
ON storage.objects FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy para authenticated users podem ler seus próprios files
CREATE POLICY "Users can read own files"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'cvs' OR bucket_id = 'job-postings');
```

---

## ✅ Verificação

Depois de criar os buckets:

1. Inicia backend: `start_backend.bat`
2. Inicia frontend: `start_frontend.bat`
3. Vai a http://localhost:3000
4. Testa Candidate flow com upload de CV
5. **Deve funcionar!** ✅

---

## 🎯 Estado Após Criação

Antes: ❌ Upload de files falha  
Depois: ✅ Upload de files funciona 100%

---

**CRIAR AGORA**: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/storage

