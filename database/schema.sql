CREATE TABLE IF NOT EXISTS scenes (
    scene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    latitude REAL,
    longitude REAL,
    resolution TEXT,
    camera_id TEXT NOT NULL,
    media_path TEXT NOT NULL,
    processed BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS detections (
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id INTEGER NOT NULL,
    class_label TEXT NOT NULL,
    confidence REAL NOT NULL,
    x_min REAL NOT NULL,
    y_min REAL NOT NULL,
    x_max REAL NOT NULL,
    y_max REAL NOT NULL,
    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scene_descriptions (
    description_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    confidence REAL NOT NULL,
    model_version TEXT NOT NULL,
    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS annotations (
    annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id INTEGER NOT NULL,
    label_type TEXT CHECK(label_type IN ('manual', 'ground_truth')),
    description TEXT,
    class_label TEXT,
    x_min REAL,
    y_min REAL,
    x_max REAL,
    y_max REAL,
    annotated_by TEXT,
    annotation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id INTEGER NOT NULL,
    dataset_type TEXT CHECK(dataset_type IN ('train', 'val', 'test')),
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scenes_timestamp ON scenes(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_class ON detections(class_label);
CREATE INDEX IF NOT EXISTS idx_annotations_type ON annotations(label_type);