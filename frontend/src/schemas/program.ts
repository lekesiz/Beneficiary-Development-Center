import { z } from 'zod';

export const programSchema = z
  .object({
    title: z
      .string()
      .min(1, 'Başlık zorunludur')
      .max(200, 'Başlık en fazla 200 karakter olabilir'),
    code: z
      .string()
      .min(1, 'Kod zorunludur')
      .max(50, 'Kod en fazla 50 karakter olabilir'),
    description: z.string().optional(),
    type: z.enum([
      'training',
      'workshop',
      'certification',
      'bootcamp',
      'mentorship',
      'other',
    ]),
    status: z
      .enum(['draft', 'published', 'active', 'completed', 'archived'])
      .default('draft'),
    start_date: z.string().min(1, 'Başlangıç tarihi zorunludur'),
    end_date: z.string().min(1, 'Bitiş tarihi zorunludur'),
    capacity: z.object({
      min: z.number().min(1, 'Minimum katılımcı sayısı 1 olmalıdır').default(1),
      max: z
        .number()
        .min(1, 'Maksimum katılımcı sayısı 1 olmalıdır')
        .default(50),
    }),
    location: z.object({
      is_online: z.boolean().default(false),
      is_hybrid: z.boolean().default(false),
      physical_location: z.string().optional(),
      online_link: z
        .string()
        .url('Geçerli bir URL giriniz')
        .optional()
        .or(z.literal('')),
    }),
    pricing: z.object({
      is_free: z.boolean().default(false),
      price: z.number().min(0, 'Fiyat 0 veya daha büyük olmalıdır').default(0),
      currency: z.string().default('EUR'),
    }),
    metadata: z.object({
      tags: z.array(z.string()).default([]),
      categories: z.array(z.string()).default([]),
      image_url: z
        .string()
        .url('Geçerli bir URL giriniz')
        .optional()
        .or(z.literal('')),
    }),
    coordinator_id: z.number().optional(),
    additional_info: z.string().optional(),
  })
  .refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
    message: 'Bitiş tarihi başlangıç tarihinden önce olamaz',
    path: ['end_date'],
  })
  .refine((data) => data.capacity.max >= data.capacity.min, {
    message: 'Maksimum katılımcı sayısı minimum katılımcı sayısından az olamaz',
    path: ['capacity', 'max'],
  })
  .refine((data) => !data.pricing.is_free || data.pricing.price === 0, {
    message: 'Ücretsiz programın fiyatı 0 olmalıdır',
    path: ['pricing', 'price'],
  });

export type ProgramFormData = z.infer<typeof programSchema>;
