// Add click event listeners to the buttons, call the functions passed in
$submitBtn = document.getElementById("submitBtn")
$submitBtn.addEventListener("click", submitUserInput);

//populate select element with possible parent category values
parentCategoriesUrl = "/fetch_parent_categories";
Plotly.d3.json(parentCategoriesUrl, function (error, response) {
    if (error) console.log(error);
    parentCategoryList = ['All Categories'];
    for (var i = 0; i < response.length; i++) {
        parentCategoryList.push(response[i]);
    }

    $parentCategorySelectListComplete = document.getElementById("parentCategorySelectComplete");
    for (var i = 0; i < parentCategoryList.length; i++) {
        var $optionComplete = document.createElement("option");
        $optionComplete.value = parentCategoryList[i];
        $optionComplete.text = parentCategoryList[i];
        $parentCategorySelectListComplete.appendChild($optionComplete);
    }

    //populate select element with possible category values
    categoriesCompleteUrl = `/fetch_categories_month_started/All Categories/`;
    Plotly.d3.json(categoriesCompleteUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Subcategories'];
        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }

        $categorySelectListComplete = document.getElementById("categorySelectComplete");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionComplete = document.createElement("option");
            $optionComplete.value = categoryList[i];
            $optionComplete.text = categoryList[i];
            $categorySelectListComplete.appendChild($optionComplete);
        }
    });
});

function optionChangedParentCategoryComplete(selectListId){
    $parentCategorySelectComplete = document.getElementById("parentCategorySelectComplete")
    parentCategoryComplete = $parentCategorySelectComplete.value
    categoriesCompleteUrl = `/fetch_categories_length_campaign/${parentCategoryComplete}`;
    
    Plotly.d3.json(categoriesCompleteUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];

        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }

        $categorySelectComplete = document.getElementById("categorySelectComplete");
        removeOptions($categorySelectComplete)

        for (var i = 0; i < categoryList.length; i++) {
            var $optionComplete = document.createElement("option");
            $optionComplete.value = categoryList[i];
            $optionComplete.text = categoryList[i];
            $categorySelectComplete.appendChild($optionComplete);
        }
    });
}

function removeOptions(selectbox) {
    var i;
    for (i = selectbox.options.length - 1; i >= 0; i--) {
        selectbox.remove(i);
    }
}

function submitUserInput(){
    event.preventDefault();
    $titleFormComplete = document.getElementById("subject")
    titleText = $titleFormComplete.value
    console.log(titleText)
}