import { rest } from 'msw'
import { mockBeneficiary, mockBeneficiaryList } from './beneficiary'
import { BeneficiaryListResponse, BeneficiaryStatistics } from '@/types/beneficiary'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

export const handlers = [
  // Get all beneficiaries
  rest.get(`${API_URL}/beneficiaries`, (req, res, ctx) => {
    const page = Number(req.url.searchParams.get('page')) || 1
    const perPage = Number(req.url.searchParams.get('per_page')) || 20
    const search = req.url.searchParams.get('search')
    const status = req.url.searchParams.get('status')

    let filteredList = [...mockBeneficiaryList]

    // Apply search filter
    if (search) {
      filteredList = filteredList.filter(b => 
        b.full_name.toLowerCase().includes(search.toLowerCase()) ||
        b.email?.toLowerCase().includes(search.toLowerCase())
      )
    }

    // Apply status filter
    if (status) {
      filteredList = filteredList.filter(b => b.status === status)
    }

    const start = (page - 1) * perPage
    const end = start + perPage
    const paginatedList = filteredList.slice(start, end)

    const response: BeneficiaryListResponse = {
      beneficiaries: paginatedList,
      pagination: {
        page,
        per_page: perPage,
        total: filteredList.length,
        pages: Math.ceil(filteredList.length / perPage),
      },
    }

    return res(ctx.status(200), ctx.json(response))
  }),

  // Get beneficiary by ID
  rest.get(`${API_URL}/beneficiaries/:id`, (req, res, ctx) => {
    const { id } = req.params
    const beneficiary = mockBeneficiaryList.find(b => b.id === Number(id))

    if (!beneficiary) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Beneficiary not found' })
      )
    }

    return res(
      ctx.status(200),
      ctx.json({ beneficiary })
    )
  }),

  // Create beneficiary
  rest.post(`${API_URL}/beneficiaries`, async (req, res, ctx) => {
    const data = await req.json()

    if (!data.first_name || !data.last_name) {
      return res(
        ctx.status(400),
        ctx.json({ error: 'First name and last name are required' })
      )
    }

    const newBeneficiary = {
      ...mockBeneficiary,
      id: mockBeneficiaryList.length + 1,
      ...data,
      full_name: `${data.first_name} ${data.last_name}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    return res(
      ctx.status(201),
      ctx.json({
        message: 'Beneficiary created successfully',
        beneficiary: newBeneficiary,
      })
    )
  }),

  // Update beneficiary
  rest.put(`${API_URL}/beneficiaries/:id`, async (req, res, ctx) => {
    const { id } = req.params
    const data = await req.json()
    const beneficiary = mockBeneficiaryList.find(b => b.id === Number(id))

    if (!beneficiary) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Beneficiary not found' })
      )
    }

    const updatedBeneficiary = {
      ...beneficiary,
      ...data,
      updated_at: new Date().toISOString(),
    }

    return res(
      ctx.status(200),
      ctx.json({
        message: 'Beneficiary updated successfully',
        beneficiary: updatedBeneficiary,
      })
    )
  }),

  // Delete beneficiary
  rest.delete(`${API_URL}/beneficiaries/:id`, (req, res, ctx) => {
    const { id } = req.params
    const beneficiary = mockBeneficiaryList.find(b => b.id === Number(id))

    if (!beneficiary) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Beneficiary not found' })
      )
    }

    return res(
      ctx.status(200),
      ctx.json({ message: 'Beneficiary deleted successfully' })
    )
  }),

  // Get statistics
  rest.get(`${API_URL}/beneficiaries/statistics`, (req, res, ctx) => {
    const statistics: BeneficiaryStatistics = {
      total: mockBeneficiaryList.length,
      by_status: {
        active: 1,
        inactive: 1,
        completed: 1,
        suspended: 0,
      },
      by_employment: {
        employed: 2,
        unemployed: 0,
        student: 0,
        self_employed: 1,
        retired: 0,
        other: 0,
      },
      by_education: {
        bachelor: 2,
        master: 1,
        doctorate: 0,
        high_school: 0,
        no_diploma: 0,
        primary: 0,
        secondary: 0,
        other: 0,
      },
      by_age: {
        '18-25': 0,
        '26-35': 3,
        '36-45': 0,
        '46-55': 0,
        '56+': 0,
      },
    }

    return res(
      ctx.status(200),
      ctx.json({ statistics })
    )
  }),

  // Add note
  rest.post(`${API_URL}/beneficiaries/:id/notes`, async (req, res, ctx) => {
    const { id } = req.params
    const { note } = await req.json()
    const beneficiary = mockBeneficiaryList.find(b => b.id === Number(id))

    if (!beneficiary) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Beneficiary not found' })
      )
    }

    if (!note) {
      return res(
        ctx.status(400),
        ctx.json({ error: 'Note text is required' })
      )
    }

    const updatedBeneficiary = {
      ...beneficiary,
      notes: [
        ...beneficiary.notes,
        {
          id: String(beneficiary.notes.length + 1),
          text: note,
          created_by: 1,
          created_at: new Date().toISOString(),
        },
      ],
    }

    return res(
      ctx.status(200),
      ctx.json({
        message: 'Note added successfully',
        beneficiary: updatedBeneficiary,
      })
    )
  }),

  // Add tag
  rest.post(`${API_URL}/beneficiaries/:id/tags`, async (req, res, ctx) => {
    const { id } = req.params
    const { tag } = await req.json()
    const beneficiary = mockBeneficiaryList.find(b => b.id === Number(id))

    if (!beneficiary) {
      return res(
        ctx.status(404),
        ctx.json({ error: 'Beneficiary not found' })
      )
    }

    if (!tag) {
      return res(
        ctx.status(400),
        ctx.json({ error: 'Tag is required' })
      )
    }

    const updatedBeneficiary = {
      ...beneficiary,
      tags: [...new Set([...beneficiary.tags, tag])],
    }

    return res(
      ctx.status(200),
      ctx.json({
        message: 'Tag added successfully',
        beneficiary: updatedBeneficiary,
      })
    )
  }),
]