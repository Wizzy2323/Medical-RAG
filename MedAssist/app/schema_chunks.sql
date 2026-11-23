-- Run once against the `medassist` database
CREATE TABLE IF NOT EXISTS document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    user_id INT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    INDEX idx_chunks_user (user_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
