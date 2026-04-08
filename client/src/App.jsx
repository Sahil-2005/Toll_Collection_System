import { useEffect, useMemo, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const inputRef = useRef(null)
  const [activeTab, setActiveTab] = useState('process')
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [usersLoading, setUsersLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState('')
  const [usersError, setUsersError] = useState('')
  const [result, setResult] = useState(null)
  const [users, setUsers] = useState([])
  const [selectedPlate, setSelectedPlate] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [previewSize, setPreviewSize] = useState({ width: 0, height: 0 })

  const detectedPlate = result?.plate_text || ''

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      setPreviewSize({ width: 0, height: 0 })
      return
    }

    const objectUrl = URL.createObjectURL(file)
    setPreviewUrl(objectUrl)

    return () => URL.revokeObjectURL(objectUrl)
  }, [file])

  useEffect(() => {
    fetchUsers()
  }, [])

  useEffect(() => {
    if (!detectedPlate) {
      return
    }
    fetchUserByPlate(detectedPlate)
  }, [detectedPlate])

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

  const filteredUsers = useMemo(() => {
    const query = selectedPlate.trim().toUpperCase()
    if (!query) {
      return users
    }
    return users.filter((user) => user.plate_number.includes(query))
  }, [users, selectedPlate])

  const previewBboxStyle = useMemo(() => {
    const bbox = result?.bbox
    if (!bbox || bbox.length !== 4 || !previewSize.width || !previewSize.height) {
      return null
    }

    const [x1, y1, x2, y2] = bbox
    const boxWidth = Math.max(0, x2 - x1)
    const boxHeight = Math.max(0, y2 - y1)

    return {
      left: `${(x1 / previewSize.width) * 100}%`,
      top: `${(y1 / previewSize.height) * 100}%`,
      width: `${(boxWidth / previewSize.width) * 100}%`,
      height: `${(boxHeight / previewSize.height) * 100}%`,
    }
  }, [result, previewSize])

  async function fetchUsers() {
    setUsersLoading(true)
    setUsersError('')

    try {
      const response = await fetch(`${API_BASE_URL}/api/users`)
      if (!response.ok) {
        throw new Error(`Users API returned ${response.status}`)
      }
      const data = await response.json()
      setUsers(data.users || [])
    } catch (usersFetchError) {
      setUsersError(usersFetchError.message || 'Unable to load users.')
    } finally {
      setUsersLoading(false)
    }
  }

  async function fetchUserByPlate(plateNumber) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${encodeURIComponent(plateNumber)}`)
      if (!response.ok) {
        throw new Error(`Lookup API returned ${response.status}`)
      }
      const data = await response.json()
      setSelectedUser(data.user || null)
    } catch {
      setSelectedUser(null)
    }
  }

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
      if (data.plate_text) {
        setSelectedPlate(data.plate_text)
      }
      if (data.user) {
        setSelectedUser(data.user)
      }
      fetchUsers()
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

  function selectUser(user) {
    setSelectedPlate(user.plate_number)
    setSelectedUser(user)
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

        <div className="mb-6 inline-flex rounded-xl border border-slate-700/70 bg-slate-900/60 p-1">
          <button
            type="button"
            onClick={() => setActiveTab('process')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === 'process'
                ? 'bg-cyan-400 text-slate-900'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            }`}
          >
            Image Processing
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('users')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === 'users'
                ? 'bg-cyan-400 text-slate-900'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            }`}
          >
            Registered Users
          </button>
        </div>

        {activeTab === 'process' ? (
          <>
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

            <section className="grid gap-6 xl:grid-cols-3">
              <article className="overflow-hidden rounded-2xl border border-slate-700/50 bg-slate-900/50 shadow-xl backdrop-blur xl:col-span-2">
                <div className="border-b border-slate-700/50 px-5 py-3">
                  <h2 className="text-sm font-semibold tracking-wide text-slate-200">Uploaded Image</h2>
                </div>
                <div className="flex min-h-72 items-center justify-center bg-slate-950/50 p-4">
                  {previewUrl ? (
                    <div className="relative inline-block max-w-full">
                      <img
                        src={previewUrl}
                        alt="Uploaded vehicle"
                        onLoad={(event) => {
                          setPreviewSize({
                            width: event.currentTarget.naturalWidth,
                            height: event.currentTarget.naturalHeight,
                          })
                        }}
                        className="max-h-[26rem] max-w-full rounded-lg object-contain"
                      />

                      {previewBboxStyle ? (
                        <div
                          style={previewBboxStyle}
                          className="pointer-events-none absolute border-[3px] border-emerald-400 shadow-[0_0_0_1px_rgba(16,185,129,0.4)]"
                        />
                      ) : null}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">Upload an image to preview it here.</p>
                  )}
                </div>
              </article>

              <div className="space-y-6">
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

                <article className="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-6 shadow-xl backdrop-blur">
                  <h2 className="mb-4 text-lg font-semibold text-white">Detected User Details</h2>
                  {selectedUser ? (
                    <div className="space-y-3 text-sm">
                      <p className="text-slate-300">
                        <span className="text-slate-400">Plate:</span> {selectedUser.plate_number}
                      </p>
                      <p className="text-slate-300">
                        <span className="text-slate-400">Owner:</span> {selectedUser.owner_name}
                      </p>
                      <p className="text-slate-300">
                        <span className="text-slate-400">Wallet:</span> Rs {Number(selectedUser.wallet_balance).toFixed(2)}
                      </p>
                      <p className="text-slate-300">
                        <span className="text-slate-400">Active:</span> {selectedUser.is_active ? 'Yes' : 'No'}
                      </p>
                      <p className="text-xs text-slate-500">Source: {selectedUser.source_table}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">Upload an image to fetch matched user details.</p>
                  )}
                </article>
              </div>
            </section>
          </>
        ) : (
          <section className="grid gap-6 xl:grid-cols-3">
            <article className="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-5 shadow-xl backdrop-blur xl:col-span-2">
              <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <h2 className="text-lg font-semibold text-white">All Registered Users</h2>
                <div className="flex gap-2">
                  <input
                    value={selectedPlate}
                    onChange={(event) => setSelectedPlate(event.target.value.toUpperCase())}
                    placeholder="Search by plate"
                    className="rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-300/50 placeholder:text-slate-500 focus:ring-2"
                  />
                  <button
                    type="button"
                    onClick={fetchUsers}
                    className="rounded-lg bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-300"
                  >
                    Refresh
                  </button>
                </div>
              </div>

              {usersLoading ? <p className="text-sm text-cyan-300">Loading users...</p> : null}
              {usersError ? <p className="text-sm text-rose-300">{usersError}</p> : null}

              <div className="max-h-[28rem] overflow-auto rounded-xl border border-slate-800">
                <table className="w-full min-w-[42rem] text-left text-sm">
                  <thead className="sticky top-0 bg-slate-950/95 text-slate-300">
                    <tr>
                      <th className="px-3 py-2">Plate</th>
                      <th className="px-3 py-2">Owner</th>
                      <th className="px-3 py-2">Wallet</th>
                      <th className="px-3 py-2">Active</th>
                      <th className="px-3 py-2">Table</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => {
                      const isDetected = user.plate_number === detectedPlate
                      return (
                        <tr
                          key={`${user.source_table}-${user.plate_number}`}
                          onClick={() => selectUser(user)}
                          className={`cursor-pointer border-t border-slate-800 transition hover:bg-slate-800/70 ${
                            isDetected ? 'bg-emerald-600/20' : ''
                          }`}
                        >
                          <td className="px-3 py-2 font-medium text-cyan-300">{user.plate_number}</td>
                          <td className="px-3 py-2 text-slate-200">{user.owner_name}</td>
                          <td className="px-3 py-2 text-slate-200">Rs {Number(user.wallet_balance).toFixed(2)}</td>
                          <td className="px-3 py-2 text-slate-200">{user.is_active ? 'Yes' : 'No'}</td>
                          <td className="px-3 py-2 text-xs text-slate-400">{user.source_table}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </article>

            <article className="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-6 shadow-xl backdrop-blur">
              <h2 className="mb-4 text-lg font-semibold text-white">Selected User</h2>
              {selectedUser ? (
                <div className="space-y-3 text-sm">
                  <p className="text-slate-300">
                    <span className="text-slate-400">Plate:</span> {selectedUser.plate_number}
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Owner:</span> {selectedUser.owner_name}
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Wallet:</span> Rs {Number(selectedUser.wallet_balance).toFixed(2)}
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Active:</span> {selectedUser.is_active ? 'Yes' : 'No'}
                  </p>
                  <p className="text-xs text-slate-500">Source: {selectedUser.source_table}</p>
                </div>
              ) : (
                <p className="text-sm text-slate-500">Click any row to inspect user details side by side.</p>
              )}

              {detectedPlate ? (
                <p className="mt-5 rounded-lg bg-emerald-500/15 px-3 py-2 text-xs text-emerald-300 ring-1 ring-emerald-400/30">
                  Last detected plate: {detectedPlate}
                </p>
              ) : null}
            </article>
          </section>
        )}
      </div>
    </main>
  )
}

export default App
