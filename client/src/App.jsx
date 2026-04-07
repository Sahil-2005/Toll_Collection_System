import { useEffect, useMemo, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return
    }

    const objectUrl = URL.createObjectURL(file)
    setPreviewUrl(objectUrl)

    return () => URL.revokeObjectURL(objectUrl)
  }, [file])

  const statusStyles = useMemo(() => {
    if (!result) {
      return {
        text: 'text-slate-400',
        badge: 'bg-slate-600/40 text-slate-200 ring-slate-500/50',
      }
    }

    if (result.status === 'Success') {
      return {
        text: 'text-emerald-300',
        badge: 'bg-emerald-500/20 text-emerald-200 ring-emerald-400/40',
      }
    }

    return {
      text: 'text-rose-300',
      badge: 'bg-rose-500/20 text-rose-200 ring-rose-400/40',
    }
  }, [result])

  async function handleUpload(selectedFile) {
    if (!selectedFile) {
      return
    }

    setFile(selectedFile)
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE_URL}/api/process-image`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (uploadError) {
      setError(uploadError.message || 'Failed to process image.')
    } finally {
      setLoading(false)
    }
  }

  function onFileChange(event) {
    const selectedFile = event.target.files?.[0]
    handleUpload(selectedFile)
  }

  function openFileDialog() {
    inputRef.current?.click()
  }

  function onDrop(event) {
    event.preventDefault()
    setDragActive(false)
    const droppedFile = event.dataTransfer.files?.[0]
    handleUpload(droppedFile)
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#1e293b_0%,_#0f172a_35%,_#020617_80%)] px-4 py-10 text-slate-100 sm:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <header className="mb-8">
          <p className="mb-2 inline-flex rounded-full bg-cyan-400/10 px-3 py-1 text-xs tracking-widest text-cyan-300 ring-1 ring-cyan-300/30">
            AUTOMATIC TOLL COLLECTION
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            ALPR Processing Dashboard
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-300 sm:text-base">
            Upload a vehicle image to detect the license plate and process the toll instantly.
          </p>
        </header>

        <section className="mb-8 rounded-2xl border border-slate-700/50 bg-slate-900/50 p-5 shadow-2xl backdrop-blur">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={onFileChange}
            className="hidden"
          />

          <div
            onDragOver={(event) => {
              event.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={`rounded-xl border-2 border-dashed p-8 text-center transition ${
              dragActive
                ? 'border-cyan-300 bg-cyan-300/10'
                : 'border-slate-600 bg-slate-950/40'
            }`}
          >
            <p className="text-lg font-medium text-slate-100">Drop your image here</p>
            <p className="mt-1 text-sm text-slate-400">or click to browse your files</p>
            <button
              type="button"
              onClick={openFileDialog}
              className="mt-5 rounded-lg bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-slate-900 transition hover:bg-cyan-300"
            >
              Choose Image
            </button>
          </div>

          {loading ? (
            <p className="mt-4 text-sm text-cyan-300">Processing image with YOLOv8 + EasyOCR...</p>
          ) : null}
          {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <article className="overflow-hidden rounded-2xl border border-slate-700/50 bg-slate-900/50 shadow-xl backdrop-blur">
            <div className="border-b border-slate-700/50 px-5 py-3">
              <h2 className="text-sm font-semibold tracking-wide text-slate-200">Uploaded Image</h2>
            </div>
            <div className="flex min-h-72 items-center justify-center bg-slate-950/50 p-4">
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Uploaded vehicle"
                  className="max-h-[26rem] w-full rounded-lg object-contain"
                />
              ) : (
                <p className="text-sm text-slate-500">Upload an image to preview it here.</p>
              )}
            </div>
          </article>

          <article className="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-6 shadow-xl backdrop-blur">
            <h2 className="mb-5 text-xl font-semibold text-white">Toll Receipt</h2>

            <div className="space-y-4 text-sm">
              <div className="rounded-lg bg-slate-950/50 p-4">
                <p className="text-slate-400">Detected Plate</p>
                <p className="mt-1 text-2xl font-semibold tracking-wider text-cyan-300">
                  {result?.plate_text || '----'}
                </p>
              </div>

              <div className="rounded-lg bg-slate-950/50 p-4">
                <p className="text-slate-400">Transaction Status</p>
                <span
                  className={`mt-2 inline-flex rounded-full px-3 py-1 text-sm font-medium ring-1 ${statusStyles.badge}`}
                >
                  {result?.status || 'Waiting'}
                </span>
                <p className={`mt-2 ${statusStyles.text}`}>{result?.message || 'No transaction yet'}</p>
              </div>

              <div className="rounded-lg bg-slate-950/50 p-4">
                <p className="text-slate-400">Updated Wallet Balance</p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {result?.updated_balance !== null && result?.updated_balance !== undefined
                    ? `Rs ${Number(result.updated_balance).toFixed(2)}`
                    : '--'}
                </p>
              </div>
            </div>
          </article>
        </section>
      </div>
    </main>
  )
}

export default App
