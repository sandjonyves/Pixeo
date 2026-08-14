'use client'

import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function AdminGalleriesScreen() {
  const { state, setCollectionStatus } = useGallery()
  const { notify } = useToast()

  const hide = (id: string, name: string) => {
    setCollectionStatus(id, 'hidden')
    notify(`“${name}” set to hidden`)
  }

  return (
    <>
      <h1>Galleries</h1>
      <p className="page-lead">Platform-wide collection moderation.</p>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Slug</th>
            <th>Status</th>
            <th>Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {state.collections.map((collection) => (
            <tr key={collection.id}>
              <td>{collection.name}</td>
              <td>{collection.slug}</td>
              <td>
                <span className={`status-pill ${collection.status}`}>{collection.status}</span>
              </td>
              <td>{new Date(collection.updatedAt).toLocaleDateString('fr-FR')}</td>
              <td>
                {collection.status !== 'hidden' && (
                  <button
                    type="button"
                    className="outline-button"
                    onClick={() => hide(collection.id, collection.name)}
                  >
                    Force hidden
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
