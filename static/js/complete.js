// Add click event listeners to the buttons, call the functions passed in
$submitBtn = document.getElementById("submitBtn")
$submitBtn.addEventListener("click", submitUserInput);

$resetBtn = document.getElementById("resetBtn")
$resetBtn.addEventListener("click", resetUserInput);

//populate select element with possible parent category values
parentCategoriesUrl = "/fetch_parent_categories";
Plotly.d3.json(parentCategoriesUrl, function (error, response) {
    if (error) console.log(error);
    parentCategoryList = [];
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
    categoriesCompleteUrl = `/fetch_categories_month_started/${$parentCategorySelectListComplete.value}/`;
    Plotly.d3.json(categoriesCompleteUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = [];
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

    monthList = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    $monthSelectListComplete = document.getElementById("monthSelectComplete");
    for (var i = 0; i < monthList.length; i++) {
        var $optionComplete = document.createElement("option");
        $optionComplete.value = monthList[i];
        $optionComplete.text = monthList[i];
        $monthSelectListComplete.appendChild($optionComplete);
    }

    countryList = ["Australia","Austria","Belgium","Canada","Denmark","France","Germany","Great Britain","Hong Kong","Ireland","Italy","Japan","Luxembourg","Mexico","Netherlands","New Zealand","Norway","Singapore","Spain","Sweeden","Switzerland","United States",]
    $countrySelectListComplete = document.getElementById("countrySelectComplete");
    for (var i = 0; i < countryList.length; i++) {
        var $optionComplete = document.createElement("option");
        $optionComplete.value = countryList[i];
        $optionComplete.text = countryList[i];
        $countrySelectListComplete.appendChild($optionComplete);
    }
});

function optionChangedParentCategoryComplete(selectListId){
    $parentCategorySelectComplete = document.getElementById("parentCategorySelectComplete")
    parentCategoryComplete = $parentCategorySelectComplete.value
    categoriesCompleteUrl = `/fetch_categories_length_campaign/${parentCategoryComplete}`;
    
    Plotly.d3.json(categoriesCompleteUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = [];

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
    for (var i = selectbox.options.length - 1; i >= 0; i--) {
        selectbox.remove(i);
    }
}

function submitUserInput(){
    event.preventDefault();

    var titleText = document.getElementById("subject").value
    var blurbText = document.getElementById("message").value
    var goalText = document.getElementById("inputGoal").value
    var campaignLengthText = document.getElementById("inputLengthCampaign").value
    var startMonth = document.getElementById("monthSelectComplete").value
    var parentCategory = document.getElementById("parentCategorySelectComplete").value
    var category = document.getElementById("categorySelectComplete").value
    var country = document.getElementById("countrySelectComplete").value

    blurbText = blurbText.replace("/","|")
    titleText = titleText.replace("/","|")
    goalText = goalText.replace("/","|")

    var predictUrl = `/predict/${titleText}/${blurbText}/${goalText}/${campaignLengthText}/${startMonth}/${parentCategory}/${category}/${country}/`;
    Plotly.d3.json(predictUrl, function(error,response){
        console.log(response)
        prediction = capitalizeFirstLetter(response.prediction)
        predictionText = "Prediction: " + prediction
        $predictionLabel = document.getElementById("predictionLabel")
        $predictionLabel.innerText = predictionText
    });
}

function resetUserInput(){}

function capitalizeFirstLetter(string) {
    return string[0].toUpperCase() + string.slice(1);
}