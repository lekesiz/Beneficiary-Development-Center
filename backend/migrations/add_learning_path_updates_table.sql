-- Add learning_path_updates table
CREATE TABLE IF NOT EXISTS learning_path_updates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    learning_path_id INTEGER NOT NULL REFERENCES learning_paths(id),
    suggested_by_user_id INTEGER REFERENCES users(id),
    
    -- Update Type
    update_type VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    
    -- Suggested Changes (JSON)
    suggested_milestones JSONB DEFAULT '[]'::jsonb,
    milestone_updates JSONB DEFAULT '{}'::jsonb,
    obsolete_milestone_ids JSONB DEFAULT '[]'::jsonb,
    reorder_map JSONB DEFAULT '{}'::jsonb,
    
    -- Reasoning and Impact
    reason TEXT,
    expected_impact VARCHAR(200),
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    approved_by_user_id INTEGER REFERENCES users(id),
    approved_at TIMESTAMP,
    applied_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- AI Analysis Context
    ai_analysis_data JSONB,
    student_metrics JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CHECK (update_type IN ('add_milestone', 'reorder', 'obsolete_milestone', 'modify_milestone')),
    CHECK (source IN ('ai', 'system', 'manual')),
    CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CHECK (status IN ('pending', 'approved', 'rejected', 'applied'))
);

-- Create indexes for performance
CREATE INDEX idx_learning_path_updates_learning_path_id ON learning_path_updates(learning_path_id);
CREATE INDEX idx_learning_path_updates_tenant_id ON learning_path_updates(tenant_id);
CREATE INDEX idx_learning_path_updates_status ON learning_path_updates(status);
CREATE INDEX idx_learning_path_updates_priority ON learning_path_updates(priority);

-- Add trigger to update updated_at
CREATE OR REPLACE FUNCTION update_learning_path_updates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_learning_path_updates_updated_at
BEFORE UPDATE ON learning_path_updates
FOR EACH ROW
EXECUTE FUNCTION update_learning_path_updates_updated_at();