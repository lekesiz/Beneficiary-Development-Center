import React, { useState, KeyboardEvent } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TagInputProps {
  value: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
  className?: string
  error?: boolean
}

export const TagInput: React.FC<TagInputProps> = ({
  value = [],
  onChange,
  placeholder = 'Add a tag...',
  className,
  error,
}) => {
  const [inputValue, setInputValue] = useState('')

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addTag()
    } else if (e.key === 'Backspace' && inputValue === '' && value.length > 0) {
      removeTag(value.length - 1)
    }
  }

  const addTag = () => {
    const tag = inputValue.trim()
    if (tag && !value.includes(tag)) {
      onChange([...value, tag])
      setInputValue('')
    }
  }

  const removeTag = (index: number) => {
    const newTags = value.filter((_, i) => i !== index)
    onChange(newTags)
  }

  return (
    <div
      className={cn(
        'flex flex-wrap gap-2 min-h-[42px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2',
        error && 'border-destructive focus-within:ring-destructive',
        className
      )}
    >
      {value.map((tag, index) => (
        <span
          key={index}
          className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary"
        >
          {tag}
          <button
            type="button"
            onClick={() => removeTag(index)}
            className="text-primary/60 hover:text-primary focus:outline-none"
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={addTag}
        placeholder={value.length === 0 ? placeholder : ''}
        className="flex-1 min-w-[120px] outline-none bg-transparent placeholder:text-muted-foreground"
      />
    </div>
  )
}