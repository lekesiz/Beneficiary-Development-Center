import { http, HttpResponse } from 'msw';

import { BeneficiaryListResponse, BeneficiaryStatistics } from '@/types/beneficiary';

import { mockBeneficiary, mockBeneficiaryList } from './beneficiary';

const API_URL = 'http://localhost:5001/api/v1';

export const handlers = [
  // Get all beneficiaries
  http.get(`${API_URL}/beneficiaries`, ({ request }) => {
    const url = new URL(request.url);
    const page = Number(url.searchParams.get('page')) || 1;
    const perPage = Number(url.searchParams.get('per_page')) || 20;
    const search = url.searchParams.get('search');
    const status = url.searchParams.get('status');

    let filteredList = [...mockBeneficiaryList];

    // Apply search filter
    if (search) {
      filteredList = filteredList.filter(
        (b) =>
          b.first_name.toLowerCase().includes(search.toLowerCase()) ||
          b.last_name.toLowerCase().includes(search.toLowerCase()) ||
          b.email.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Apply status filter
    if (status) {
      filteredList = filteredList.filter((b) => b.status === status);
    }

    const start = (page - 1) * perPage;
    const end = start + perPage;
    const paginatedList = filteredList.slice(start, end);

    const response: BeneficiaryListResponse = {
      beneficiaries: paginatedList,
      pagination: {
        page,
        per_page: perPage,
        total: filteredList.length,
        pages: Math.ceil(filteredList.length / perPage),
      },
    };

    return HttpResponse.json(response, { status: 200 });
  }),

  // Get statistics (must come before /:id to avoid conflict)
  http.get(`${API_URL}/beneficiaries/statistics`, () => {
    const statistics: BeneficiaryStatistics = {
      total: mockBeneficiaryList.length,
      by_status: {
        active: mockBeneficiaryList.filter((b) => b.status === 'active').length,
        inactive: mockBeneficiaryList.filter((b) => b.status === 'inactive').length,
        pending: mockBeneficiaryList.filter((b) => b.status === 'pending').length,
      },
      by_employment_status: {
        employed: mockBeneficiaryList.filter((b) => b.employment_status === 'employed').length,
        unemployed: mockBeneficiaryList.filter((b) => b.employment_status === 'unemployed').length,
        student: mockBeneficiaryList.filter((b) => b.employment_status === 'student').length,
        retired: mockBeneficiaryList.filter((b) => b.employment_status === 'retired').length,
      },
      recent_enrollments: 5,
      completion_rate: 75.5,
    };

    return HttpResponse.json(statistics, { status: 200 });
  }),

  // Get single beneficiary
  http.get(`${API_URL}/beneficiaries/:id`, ({ params }) => {
    const { id } = params;
    const beneficiary = mockBeneficiaryList.find((b) => b.id === Number(id));

    if (!beneficiary) {
      return HttpResponse.json({ error: 'Beneficiary not found' }, { status: 404 });
    }

    return HttpResponse.json(beneficiary, { status: 200 });
  }),

  // Create beneficiary
  http.post(`${API_URL}/beneficiaries`, async ({ request }) => {
    const body = await request.json();
    const newBeneficiary = {
      id: mockBeneficiaryList.length + 1,
      ...body,
      status: 'active',
      enrollment_count: 0,
      progress_percentage: 0,
      notes: [],
      tags: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // In real implementation, this would be saved to database
    mockBeneficiaryList.push(newBeneficiary);

    return HttpResponse.json(newBeneficiary, { status: 201 });
  }),

  // Update beneficiary
  http.put(`${API_URL}/beneficiaries/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const beneficiaryIndex = mockBeneficiaryList.findIndex((b) => b.id === Number(id));

    if (beneficiaryIndex === -1) {
      return HttpResponse.json({ error: 'Beneficiary not found' }, { status: 404 });
    }

    const updatedBeneficiary = {
      ...mockBeneficiaryList[beneficiaryIndex],
      ...body,
      updated_at: new Date().toISOString(),
    };

    mockBeneficiaryList[beneficiaryIndex] = updatedBeneficiary;

    return HttpResponse.json(updatedBeneficiary, { status: 200 });
  }),

  // Delete beneficiary
  http.delete(`${API_URL}/beneficiaries/:id`, ({ params }) => {
    const { id } = params;
    const beneficiaryIndex = mockBeneficiaryList.findIndex((b) => b.id === Number(id));

    if (beneficiaryIndex === -1) {
      return HttpResponse.json({ error: 'Beneficiary not found' }, { status: 404 });
    }

    mockBeneficiaryList.splice(beneficiaryIndex, 1);

    return new HttpResponse(null, { status: 204 });
  }),

  // Add note to beneficiary
  http.post(`${API_URL}/beneficiaries/:id/notes`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const beneficiary = mockBeneficiaryList.find((b) => b.id === Number(id));

    if (!beneficiary) {
      return HttpResponse.json({ error: 'Beneficiary not found' }, { status: 404 });
    }

    const newNote = {
      id: beneficiary.notes.length + 1,
      beneficiary_id: Number(id),
      text: body.text,
      created_by: 'Current User',
      created_at: new Date().toISOString(),
    };

    beneficiary.notes.push(newNote);

    return HttpResponse.json(newNote, { status: 201 });
  }),

  // Add tag to beneficiary
  http.post(`${API_URL}/beneficiaries/:id/tags`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const beneficiary = mockBeneficiaryList.find((b) => b.id === Number(id));

    if (!beneficiary) {
      return HttpResponse.json({ error: 'Beneficiary not found' }, { status: 404 });
    }

    if (!beneficiary.tags.includes(body.tag)) {
      beneficiary.tags.push(body.tag);
    }

    return HttpResponse.json({ message: 'Tag added successfully' }, { status: 200 });
  }),
];
