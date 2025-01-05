function getSuggestions(articleId) {
    if (!articleId) {
        console.error("Article ID is required");
        return;
    }

    fetch(`/en/admin/blog/article/suggest/${articleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Suggestions:", data);
        displaySuggestions(data);
    })
    .catch(error => {
        console.error("Error fetching suggestions:", error);
    });
}

function getSuggestionsForArticle() {
    const articleId = document.getElementById('article_id').value;
    if (!articleId) {
        console.error("Article ID is required");
        return;
    }
    getSuggestions(articleId);
}

function displaySuggestions(data) {
    // Update the UI with the suggestions
    const tagDiv = document.getElementById('tag-suggestions');
    const categoryDiv = document.getElementById('category-suggestions');
    
    // Clear previous suggestions
    tagDiv.innerHTML = '';
    categoryDiv.innerHTML = '';

    if (!data || !data.tags || !data.categories) {
        console.error('Invalid suggestions data format:', data);
        return;
    }

    // Add tag suggestions
    if (Array.isArray(data.tags)) {
        data.tags.forEach(tag => {
            if (!tag.info || !tag.info.name) {
                console.error('Invalid tag data:', tag);
                return;
            }
            
            const button = document.createElement('button');
            button.className = 'btn btn-secondary';
            button.textContent = tag.info.name;
            button.onclick = (e) => {
                e.preventDefault();
                if (tag.type === 'new') {
                    createTag(tag.info.name);
                } else {
                    addExistingTag(tag.info.id);
                }
            };
            tagDiv.appendChild(button);
        });
    }

    // Add category suggestions
    if (Array.isArray(data.categories)) {
        data.categories.forEach(category => {
            if (!category.info || !category.info.name) {
                console.error('Invalid category data:', category);
                return;
            }

            const button = document.createElement('button');
            button.className = 'btn btn-secondary';
            button.textContent = category.info.name;
            button.onclick = () => {
                if (category.type === 'new') {
                    createCategory(category.info.name);
                } else {
                    setCategory(category.info.id);
                }
            };
            categoryDiv.appendChild(button);
        });
    }
}

function createTag(tagName) {
    console.log('Creating tag with name:', tagName); // Debug log
    
    // Prevent execution if tagName is undefined or empty
    if (!tagName) {
        console.error('Tag name is required');
        return;
    }

    fetch('/en/admin/blog/article/create-tag/', {
        method: 'POST',  // Explicitly set POST method
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ 
            name: tagName,
            article_id: document.getElementById('article_id').value 
        }),
        credentials: 'same-origin'  // Include credentials
    })
    .then(async response => {
        if (!response.ok) {
            const text = await response.text();
            console.error('Server response:', text);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Tag created:", data);
        const tagSelect = document.getElementById('id_tags');
        const option = new Option(data.name, data.id, true, true);
        tagSelect.add(option);
    })
    .catch(error => {
        console.error("Error creating tag:", error);
    });
}

function createCategory(categoryName) {
    fetch(`/en/admin/blog/article/create-category/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ name: categoryName })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Category created:", data);
        // Set the new category in the category selection
        const categorySelect = document.getElementById('id_category');
        const option = new Option(data.name, data.id, true, true);
        categorySelect.add(option);
        categorySelect.value = data.id;
    })
    .catch(error => {
        console.error("Error creating category:", error);
    });
}

function addExistingTag(tagId) {
    const select = document.getElementById('id_tags');
    const option = select.querySelector(`option[value="${tagId}"]`);
    if (option) {
        option.selected = true;
    }
}

function setCategory(catId) {
    document.getElementById('id_category').value = catId;
}
