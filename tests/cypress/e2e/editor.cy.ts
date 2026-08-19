describe('Editor', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('loads the page and displays the title', () => {
    cy.get('.app-title').should('be.visible')
    cy.get('.app-title').should('contain.text', 'Tiptap Rich Text Editor')
  })

  it('shows the document UUID bar', () => {
    cy.get('.doc-bar').should('be.visible')
    cy.get('.doc-label').should('contain.text', 'Document UUID')
    cy.get('.doc-uuid code').should('not.be.empty')
  })

  it('renders the editor area', () => {
    cy.get('.tiptap-editor').should('be.visible')
    cy.get('.ProseMirror').should('exist')
  })

  it('allows typing into the editor', () => {
    cy.clearEditor()
    cy.typeIntoEditor('Hello from Cypress')
    cy.get('.ProseMirror').should('contain.text', 'Hello from Cypress')
  })

  it('displays the JSON output preview', () => {
    cy.get('.content-preview').should('be.visible')
    cy.get('.content-preview h3').should('contain.text', 'JSON Output')
    cy.get('.content-preview pre').should('not.be.empty')
  })

  it('shows the save button', () => {
    cy.get('.save-btn').should('be.visible')
    cy.get('.save-btn').should('contain.text', 'Save')
  })
})
