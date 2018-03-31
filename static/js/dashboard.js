//populate select element with possible parent category values
parentCategoriesUrl = "/fetch_parent_categories";
Plotly.d3.json(parentCategoriesUrl, function (error, response) {
    if (error) console.log(error);
    parentCategoryList = ['All Parent Categories'];
    for (var i = 0; i < response.length; i++) {
        parentCategoryList.push(response[i]);
    }
    //console.log(medalList);
    $parentCategorySelectListMonthStarted = document.getElementById("parentCategorySelectMonthStarted");
    $parentCategorySelectListLengthCampaign = document.getElementById("parentCategorySelectLengthCampaign");
    for (var i = 0; i < parentCategoryList.length; i++) {
        var $optionMonthStarted = document.createElement("option");
        $optionMonthStarted.value = categoryList[i];
        $optionMonthStarted.text = categoryList[i];
        $parentCategorySelectListMonthStarted.appendChild($optionMonthStarted);

        var $optionLengthCampaign = document.createElement("option");
        $optionLengthCampaign.value = categoryList[i];
        $optionLengthCampaign.text = categoryList[i];
        $parentCategorySelectListLengthCampaign.appendChild($optionLengthCampaign);
    }

    //populate select element with possible category values
    //use parent category to narrow down possible selections
    parentCategoryMonthStarted = $categorySelectListMonthStarted.value
    categoriesMonthStartedUrl = `/fetch_categories_month_started/${parentCategoryMonthStarted}`;
    Plotly.d3.json(categoriesMonthStartedUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];
        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }
        //console.log(medalList);
        $categorySelectListMonthStarted = document.getElementById("categorySelectMonthStarted");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionMonthStarted = document.createElement("option");
            $optionMonthStarted.value = categoryList[i];
            $optionMonthStarted.text = categoryList[i];
            $categorySelectListMonthStarted.appendChild($optionMonthStarted);
        }
    });

    parentCategoryLengthCampaign = $categorySelectListLengthCampaign.value
    categoriesLengthCampaignUrl = `/fetch_categories_length_campaign/${parentCategoryLengthCampaign}`;
    Plotly.d3.json(categoriesLengthCampaignUrl, function (error, response) {
        if (error) console.log(error);
        categoryList = ['All Categories'];
        for (var i = 0; i < response.length; i++) {
            categoryList.push(response[i]);
        }
        //console.log(medalList);
        $categorySelectListLengthCampaign = document.getElementById("categorySelectLengthCampaign");
        for (var i = 0; i < categoryList.length; i++) {
            var $optionLengthCampaign = document.createElement("option");
            $optionLengthCampaign.value = categoryList[i];
            $optionLengthCampaign.text = categoryList[i];
            $categorySelectListLengthCampaign.appendChild($optionLengthCampaign);
        }
    });
});