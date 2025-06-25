/**
 * Drag and Drop List Component
 * A simple drag-and-drop reordering component
 */
import { GripVertical } from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';

import { cn } from '@/lib/utils';

interface DragDropItem {
  id: string | number;
  content: React.ReactNode;
  data?: any;
}

interface DragDropListProps {
  items: DragDropItem[];
  onReorder: (items: DragDropItem[]) => void;
  className?: string;
  disabled?: boolean;
}

export const DragDropList: React.FC<DragDropListProps> = ({
  items,
  onReorder,
  className,
  disabled = false,
}) => {
  const [draggedItem, setDraggedItem] = useState<string | number | null>(null);
  const [dragOverItem, setDragOverItem] = useState<string | number | null>(
    null
  );

  const handleDragStart = (e: React.DragEvent, id: string | number) => {
    if (disabled) return;
    setDraggedItem(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, id: string | number) => {
    if (disabled) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverItem(id);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    if (disabled) return;
    setDragOverItem(null);
  };

  const handleDrop = (e: React.DragEvent, targetId: string | number) => {
    if (disabled) return;
    e.preventDefault();

    if (!draggedItem || draggedItem === targetId) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    const draggedIndex = items.findIndex((item) => item.id === draggedItem);
    const targetIndex = items.findIndex((item) => item.id === targetId);

    if (draggedIndex === -1 || targetIndex === -1) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    const newItems = [...items];
    const [removed] = newItems.splice(draggedIndex, 1);
    newItems.splice(targetIndex, 0, removed);

    onReorder(newItems);
    setDraggedItem(null);
    setDragOverItem(null);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    setDragOverItem(null);
  };

  return (
    <div className={cn('space-y-2', className)}>
      {items.map((item, index) => (
        <div
          key={item.id}
          draggable={!disabled}
          onDragStart={(e) => handleDragStart(e, item.id)}
          onDragOver={(e) => handleDragOver(e, item.id)}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, item.id)}
          onDragEnd={handleDragEnd}
          className={cn(
            'flex items-center p-3 bg-white border rounded-lg transition-all duration-200',
            !disabled && 'cursor-move hover:shadow-md',
            draggedItem === item.id && 'opacity-50 scale-105',
            dragOverItem === item.id && 'border-blue-400 shadow-lg',
            disabled && 'cursor-not-allowed opacity-75'
          )}
        >
          {!disabled && (
            <div className="mr-3 text-gray-400 hover:text-gray-600">
              <GripVertical className="h-5 w-5" />
            </div>
          )}
          <div className="flex-1">{item.content}</div>
          <div className="ml-2 text-sm text-gray-500 font-mono">
            #{index + 1}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DragDropList;
