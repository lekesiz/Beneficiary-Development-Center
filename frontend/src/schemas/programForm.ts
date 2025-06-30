import { z } from 'zod';

import { ProgramType, ProgramStatus } from '@/types/program';

export const programFormSchema = z
  .object({
    title: z
      .string()
      .min(1, 'Program adı zorunludur')
      .max(200, 'Program adı en fazla 200 karakter olabilir'),
    code: z.string().optional(),
    description: z.string().optional(),
    objectives: z.array(z.string()).optional(),
    program_type: z.nativeEnum(ProgramType).optional(),
    status: z.nativeEnum(ProgramStatus).optional(),
    start_date: z.string().min(1, 'Başlangıç tarihi zorunludur'),
    end_date: z.string().min(1, 'Bitiş tarihi zorunludur'),
    enrollment_start: z.string().optional(),
    enrollment_end: z.string().optional(),
    min_participants: z.number().min(1, 'Minimum katılımcı sayısı en az 1 olmalıdır').optional(),
    max_participants: z.number().min(1, 'Maksimum katılımcı sayısı en az 1 olmalıdır'),
    location: z.string().optional(),
    is_online: z.boolean().optional(),
    is_hybrid: z.boolean().optional(),
    online_link: z.string().url('Geçerli bir URL giriniz').optional().or(z.literal('')),
    price: z.number().min(0, 'Ücret 0 veya daha büyük olmalıdır').optional(),
    currency: z.string().optional(),
    tags: z.array(z.string()).optional(),
    coordinator_id: z.number().optional(),
  })
  .refine(
    (data) => {
      if (data.end_date && data.start_date) {
        return new Date(data.end_date) > new Date(data.start_date);
      }
      return true;
    },
    {
      message: 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır',
      path: ['end_date'],
    }
  )
  .refine(
    (data) => {
      if (data.min_participants && data.max_participants) {
        return data.max_participants >= data.min_participants;
      }
      return true;
    },
    {
      message: 'Maksimum katılımcı sayısı minimum sayıdan az olamaz',
      path: ['max_participants'],
    }
  );

export type ProgramFormData = z.infer<typeof programFormSchema>;
