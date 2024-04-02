if __name__ == '__main__':
    from data_management import FinancialYear, get_findata_from_csv
    from language_module import check_text
else:
    from .data_management import FinancialYear
    from .language_module import check_text

class MaterialRatioAnalysis:
    '''
    Handling the analysis of the change in raw material cost ratio (extent and reasons).
    
    Arguments:
        actual_year -> class FinancialYear (defined in: data_management module)
        base_year -> class FinancialYear (defined in: data_management module)
        additional_data -> dict of preliminary data of the analysis:
            {
            'comment_on_changes_of_product_revenues': arbevelemzes_valtozok[8],
            'products': arbevelemzes_valtozok[2],
            'products_base': arbevelemzes_valtozok[3],
            'changed_products': arbevelemzes_valtozok[9],
            'new_products': arbevelemzes_valtozok[7],
            'ceased_products': arbevelemzes_valtozok[19],
            'materials': ag_targyev,                  -> [('item', cost, 'cost', unit price, 'unit price', 'I'=goods /'N'=material), ...]
            'relevant_material': van_jelentos_ag,     -> [ True= relevant material exists /False= no relevant material, int= index in 'metarials' ]
            'materials_unit_cost_change': ar_valt,    -> [(rate, 'rate', 'I'=goods /'N'=material), ...]
            'new_materials': ujag,                    -> [('item', cost, 'cost', unit price, 'unit price', 'I'=goods /'N'=material), ...]
            'ceased_materials': megszunt_targyevben,  -> [('item', cost, 'cost', unit price, 'unit price', 'I'=goods /'N'=material), ...]
            'quantity_change': menny_valt             -> [(rate, 'rate', 'I'=goods /'N'=material), ...]
            }
    '''    
    def __init__(self, actual_year: FinancialYear, base_year: FinancialYear, additional_data: dict):
        self.raw_mat_cost_ratio_base = round(base_year.cost_ratios(ratio = "raw_material_cost")*100,1)
        self.raw_mat_cost_ratio_actual = round(actual_year.cost_ratios(ratio = "raw_material_cost")*100,1)
        # self.raw_mat_cost_ratio_base = 42.1
        # self.raw_mat_cost_ratio_actual = 42.1
        self.actual_year = actual_year
        self.base_year = base_year
        self.additional_data = additional_data

    def analyse(self):
        '''
        Engine of MaterialRatioAnalysis class. Defines change of ratio and searcehs potentional reasons of change. 
        
        Returns:
            analysis = srt -> phrased change of ratio
            reasons_dict = {key: str -> subject, value: str -> potentional reason obtained from data / phrased}
            reasons_dict_key_order = [order of keys]
            to_ask_dict = {key: str -> subject, value: str -> potentional reason with no information in data / bullets}
            to_ask_dict_key_order = [order of keys]

        '''
        if self.actual_year and self.base_year:
            if self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  > 1.005:
                text=(f'Az anyagköltséghányad {self.raw_mat_cost_ratio_base }%-ról {self.raw_mat_cost_ratio_actual }%-ra '\
                    'növekedett tárgyévben.')
                potentional_reasons = self.__define_potentional_reasons('increase')
                
            elif self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  > 1.0025:
                text=(f'Az anyagköltséghányad minimálisan, {self.raw_mat_cost_ratio_base }%-ról {self.raw_mat_cost_ratio_actual }%-ra '\
                    'növekedett tárgyévben.')
                potentional_reasons = self.__define_potentional_reasons('increase')
            
            elif self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  > 1:
                text=(f'Az anyagköltséghányad ({self.raw_mat_cost_ratio_actual }%) lényegében nem változott tárgyévben.')
                potentional_reasons = MaterialRatioAnalysis.__neutral_potentional_reasons()

            elif self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  == 1:
                text=(f'Az anyagköltséghányad ({self.raw_mat_cost_ratio_actual }%) nem változott tárgyévben.')
                potentional_reasons = MaterialRatioAnalysis.__neutral_potentional_reasons()

            elif self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  >= 0.9975:
                text=(f'Az anyagköltséghányad ({self.raw_mat_cost_ratio_actual }%) lényegében nem változott tárgyévben.')
                potentional_reasons = MaterialRatioAnalysis.__neutral_potentional_reasons()

            elif self.raw_mat_cost_ratio_actual  / self.raw_mat_cost_ratio_base  >= 0.995:
                text=(f'Az anyagköltséghányad minimálisan, {self.raw_mat_cost_ratio_base }%-ról {self.raw_mat_cost_ratio_actual }%-ra '\
                    'mérséklődött tárgyévben.')
                potentional_reasons = self.__define_potentional_reasons('decrease')
            
            else: 
                text=(f'Az anyagköltséghányad {self.raw_mat_cost_ratio_base }%-ról {self.raw_mat_cost_ratio_actual }%-ra '\
                    'csökkent tárgyévben.')
                potentional_reasons = self.__define_potentional_reasons('decrease')

            reasons_dict, reasons_dict_key_order,\
            to_as_dict, to_as_dict_key_order\
            = self.__assemble_potentional_reasons_dict(potentional_reasons)

            return text, reasons_dict, reasons_dict_key_order, to_as_dict, to_as_dict_key_order
        
        if self.actual_year and not self.base_year:
            return 'Az anyagköltséghányad változásának értékelése bázis évi adatok hiányában nem lehetséges!', [], []

    def __define_potentional_reasons(self, direction):
        '''
        Searches potentional reasons for the change of raw material cost ratio.
        Argument: direction of change of raw material cost ratio -> 'decrease' or 'increase'
        
        Returns:
        reasons -> dict
            
            keys: potential reason
            
            values: list
                    [0] None -> no effect or effect cannot be determined,
                    True -> factor directing the ratio to change in the direction (arg),
                    False -> factor directing the ratio to change contra to the direction (arg)>,
                    [1] '' if no effect / comment / 'needed_to_ask' >]}
        '''
        reasons = {
            'sellingprice_change': [None,''],
            'new_customer': [None,'needed_to_ask'], # a VEVŐ modul elkészítése után lesz információ
            'customer_structure': [None,'needed_to_ask'], # a VEVŐ modul elkészítése után lesz információ
            'new_product': [None,''],
            'ceased_product': [None,''],
            'inputprice_change': [None,''],
            'new_supplier': [None,'needed_to_ask'], # a SZÁLLÍTÓ modul elkészítése után lesz információ
            'supplier_structure': [None,'needed_to_ask'], # a SZÁLLÍTÓ modul elkészítése után lesz információ
            'new_and_ceased_material': [None,''],
            'material_structure': [None,''],
            'own_production_rate': [None,''],
            'new_technology': [None,'needed_to_ask'],
        }
        
        reasons['sellingprice_change'] = self.__check_selling_price_change_effect(direction)
        reasons['new_customer'] = self.__check_new_customer()
        reasons['customer_structure'] = self.__check_customer_structure()
        reasons['new_product'] = self.__check_new_product(direction)
        reasons['ceased_product'] = self.__check_ceased_product(direction)
        reasons['new_supplier'] = self.__check_new_supplier()
        reasons['supplier_structure'] = self.__check_supplier_structure()
        reasons['own_production_rate'] = self.__check_own_production_rate(direction)
        reasons['new_technology'] = self.__check_new_technology()
        if self.additional_data['materials'] != False:
            reasons['inputprice_change'] = self.__check_inputprice_change(direction)
            reasons['new_and_ceased_material'] = self.__check_new_and_ceased_material()
            reasons['material_structure'] = self.__check_material_structure(direction)
        else:
            reasons['inputprice_change'] = [None,'needed_to_ask']
            reasons['new_and_ceased_material'] = [None,'needed_to_ask']
            reasons['material_structure'] = [None,'needed_to_ask']

        return reasons

    def __assemble_potentional_reasons_dict(self, potentional_reasons: dict):
        '''
        Argument: potentional reasons (dictionary assembeld by method: __define_potentional_reasons)
        Returns:
            reasons_dict = {key: str -> subject, value: str -> potentional reason obtained from data}
            reasons_dict_key_order = [order of keys]
            to_ask_dict = {key: str -> subject, value: str -> potentional reason with no information in data}
            to_ask_dict_key_order = [order of keys]
        '''

        key_order = [
            'sellingprice_change',
            'new_customer',
            'customer_structure',
            'new_product',
            'ceased_product',
            'inputprice_change',
            'material_structure',
            'new_supplier',
            'supplier_structure',
            'new_and_ceased_material',
            'own_production_rate',
            'new_technology'
            ]
               
        to_ask_base = {
            'sellingprice_change': 'az egyes termékek értékesítési árának, illetve az alkalmazott árrés változása',
            'new_customer': 'új vevők, illetve az esetükben alkalmazott árrés változása',
            'customer_structure': 'a vevői szerkezet változása (amennyiben az egyes vevők esetében eltérő árrés kerül alkalmazásra)',
            'new_product': 'új, a korábbiaktól eltérő árréstartalmú tevékenységek megjelenése',
            'ceased_product': 'tárgyévben megszűnt, a jelenlegiektől eltérő árréstartalmú tevékenységek',
            'inputprice_change': 'a termeléshez felhasznált anyagok egységárának változása',
            'material_structure': 'a termeléshez felhasznált egyes, eltérő árszínvonalú anyagok mennyiségének változása',
            'new_supplier': 'új, eltérő kondíciókat alkalmazó szállítók megjelenése',
            'supplier_structure': 'a szállítói szerkezet változása (az ugyanazon terméket/szolgáltatást, eltérő kondíciókkal kínáló szállítók tekintetében)',
            'new_and_ceased_material': 'megszűnt felhasználású, vagy a termelésbe került új anyagok',
            'own_production_rate': 'a pozitív előjelű STKÁV és a saját rezsis beruházások bruttó teljesítményen belüli részaránya',
            'new_technology': 'a termelési hatékonyság javítását célzó beruházások, új technológiák bevezetése'
            }

        reasons_dict = {}
        reasons_dict_key_order = []
        to_ask_dict = {}
        to_ask_dict_key_order = []

        for key in key_order:
            if potentional_reasons[key][0] != False and potentional_reasons[key][1] != '' and potentional_reasons[key][1] != 'needed_to_ask':
                reasons_dict.update({key: potentional_reasons[key][1]})
                reasons_dict_key_order.append(key)
            elif potentional_reasons[key][0] != False and potentional_reasons[key][1] == 'needed_to_ask':
                to_ask_dict.update({key: to_ask_base[key]})
                to_ask_dict_key_order.append(key)

        return reasons_dict, reasons_dict_key_order, to_ask_dict, to_ask_dict_key_order

    @staticmethod
    def __neutral_potentional_reasons():
        reasons = {
            'sellingprice_change': [None,''],
            'new_customer': [None,''],
            'customer_structure': [None,''],
            'new_product': [None,''],
            'ceased_product': [None,''],
            'inputprice_change': [None,''],
            'new_supplier': [None,''],
            'supplier_structure': [None,''],
            'new_and_ceased_material': [None,''],
            'material_structure': [None,''],
            'own_production_rate': [None,''],
            'new_technology': [None,''],
        }
        return reasons

    @staticmethod
    def remove_goods(material_list, sub_idx):
        '''
        Removes materials with 'I' flag (goods) from list
        Arguments:
            material_list: list
            sub_idx: num / index of flag in list item
        '''
        material_list_temp = []
        for item in material_list:
            if item[sub_idx] == 'N':
                material_list_temp.append(item)
        return material_list_temp

    def __check_selling_price_change_effect(self, direction):       
        result = [None,'']

        # invers relation: prices/margins increase -> cost ratio decreases (in this case reasons dict. will result True)
        if direction == 'decrease': # raw mat. cost ratio decreases/improves
            ratio_direction = ['csökkenését', 'növelésére']
        elif direction == 'increase': # raw mat. cost ratio increases/deteriorates
            ratio_direction = ['emelkedését', 'csökkenésére']

        commented_products_with_price = [] # items: lists -> [product with comments on prices, <user comments on changes of revenues>]
        changed_products = [] # items: products with changed revenue
        for idx, item in enumerate(self.additional_data['comment_on_changes_of_product_revenues']):
            if item != False:
                changed_products.append(self.additional_data['products'][idx][0])
                comment = item[0] + item[1] + item[2]
                if check_text(comment, check = 'includes_price'):
                    commented_products_with_price.append((self.additional_data['products'][idx][0], comment))
        
        for idx, item in enumerate(self.additional_data['changed_products']):
            if item != False:
                if self.additional_data['products'][idx][0] not in changed_products:
                    changed_products.append(self.additional_data['products'][idx][0])
       
        if changed_products != []: # else: changed_products == []: returns -> 'sellingprice_change': [None,'']
            
            if len(changed_products) == 1: # revenue of one product has changed
                result[1] = f'Egy adott termék ({changed_products[0]}) esetében említésre méltó változás'\
                    f' történt annak árbevételében. Mindez, a termék esetében alkalmazott, más termékekhez viszonyított árrés függvényében'\
                    f' okozhatta az anyagköltséghányad {ratio_direction[0]}.'
            
            else: # revenue of more products has changed
                changed_products_list = ''
                for item in changed_products:
                    changed_products_list += (item +', ')
                changed_products_list = changed_products_list[:-2]

                result[1] = f'Több adott termék ({changed_products[0]}) esetében említésre méltó változás'\
                    f' történt azokak árbevételében. Mindez, a termékek esetében alkalmazott, más termékekhez viszonyított árrés függvényében'\
                    f' okozhatta az anyagköltséghányad {ratio_direction[0]}.'

            if len(commented_products_with_price) == 1: # revenue of one product has changed, commented, comment refers to price
                comments = []
                comments.append(commented_products_with_price[0][1])
                              
                if check_text(commented_products_with_price[0][1], check='direction') == None:
                    result[0] = None
                    comments.append('')
                elif check_text(commented_products_with_price[0][1], check='direction') == direction:
                    result[0] = False
                    comments.append('')
                elif check_text(commented_products_with_price[0][1], check='direction') != direction:
                    result[0] = True
                    comments.append(', esetlegesen erre utaló')
                
                result[1] += (f' Az árbevétel elemzésénél a következő{comments[1]} felhasználói megjegyzés'\
                                                      f' szerepel: "... {comments[0]} ..."')

            elif len(commented_products_with_price) >= 1: # revenue of more products has changed, some of them commented, comment refers to price
                result[1] += (' Az árbevétel elemzésénél, az érintett termékek esetében a következő felhasználói'\
                                                      ' megjegyzések szerepelnek:')
                reasons_dump = []
                for item in commented_products_with_price:
                    
                    comments = []
                    comments.append(item[1])
                                
                    if check_text(item[1], check='direction') == None:
                        reasons_dump.append(None)
                        result[1] += (f'- {item[0]}: "... {comments[0]} ..."\n')
                    elif check_text(item[1], check='direction') != direction:
                        reasons_dump.append(True)
                        comments.append(f', amely megjegyzés az árrés {ratio_direction[1]} utalhat')
                        result[1] += (f'\n- {item[0]}: "... {comments[0]} ..."{comments[1]}')
                    elif check_text(item[1], check='direction') == direction:
                        reasons_dump.append(False)
              
                if reasons_dump == []:
                    result[0] = None
                elif True in reasons_dump:
                    result[0] = True
                else:
                    result[0] = False

        return(result)

    def __check_new_customer(self):
        result = [None,'needed_to_ask']
        return(result)
        
    def __check_customer_structure(self):
        result = [None,'needed_to_ask']
        return(result)

    def __check_new_product(self, direction):
        result = [None,'']

        if self.additional_data['new_products'] == False:
            return [None,'needed_to_ask']

        if self.additional_data['new_products'] != []:

            if direction == 'decrease':
                ratio_direction = ['csökkenésére']
            elif direction == 'increase':
                ratio_direction = ['emelkedésére']

            new_products = [item[0] for idx, item in enumerate(self.additional_data['new_products'])]
            new_products_list = ''
            for item in new_products:
                new_products_list += (item +', ')
            new_products_list = new_products_list[:-2]

            if len(self.additional_data['new_products']) == 1:
                result[1] = f'Tárgyévben egy új tevékenység ({new_products_list}) jelent meg a gazdálkodásban,'\
                    f' melynek árréstartalma hathatott az anyagköltséghányad {ratio_direction[0]}.'
            else:
                result[1] = f'Tárgyévben több új tevékenység ({new_products_list}) is megjelent a gazdálkodásban,'\
                    f' melyek árréstartalma hathatott az anyagköltséghányad {ratio_direction[0]}.'

        return(result)

    def __check_ceased_product(self, direction):
        result = [None,'']

        if self.additional_data['ceased_products'] != []:

            if direction == 'decrease':
                ratio_direction = ['csökkenésére']
            elif direction == 'increase':
                ratio_direction = ['emelkedésére']

            ceased_products = [item[0] for idx, item in enumerate(self.additional_data['ceased_products'])]
            ceased_products_list = ''
            for item in ceased_products:
                ceased_products_list += (item +', ')
            ceased_products_list = ceased_products_list[:-2]

            if len(self.additional_data['ceased_products']) == 1:
                result[1] = f'Tárgyévben egy tevékenység ({ceased_products_list}) kiesett a tevékenységek köréből,'\
                    f' melynek árréstartalma hathatott az anyagköltséghányad {ratio_direction[0]}.'
            else:
                result[1] = f'Tárgyévben több tevékenység ({ceased_products_list}) is kiesett a tevékenységek köréből,'\
                    f' melyek árréstartalma hathatott az anyagköltséghányad {ratio_direction[0]}.'

        return(result)

    def __check_inputprice_change(self, direction):      
        result = [None,'']

        # direct relation: input prices decrease -> cost ratio decreases (in this case reasons dict. will result True)
        if direction == 'decrease': # raw mat. cost ratio decreases/improves
            price_direction = ['mérséklődött', 'csökkenését']
        elif direction == 'increase': # raw mat. cost ratio increases/deteriorates
            price_direction = ['nőtt', 'emelkedését']

        materials = MaterialRatioAnalysis.remove_goods(self.additional_data['materials'], 5)
        materials_unit_cost_change = MaterialRatioAnalysis.remove_goods(self.additional_data['materials_unit_cost_change'], 2)
        relevant_material = self.additional_data['relevant_material']

        possible_materials = [] # materials which unit cost change in the same direction as of the material ratio; [('name', True = relevant material / False)]
        for idx, item in enumerate(materials_unit_cost_change):
            if (item[0] < 0 and direction == 'decrease') or (item[0] > 0 and direction == 'increase'):
                if relevant_material[0] and idx == relevant_material[1]:
                    possible_materials.append((materials[idx][0], True))
                else:
                    possible_materials.append((materials[idx][0], False))

        if len(materials) == 0:
            return [None, 'needed_to_ask']
        
        if len(possible_materials) == 1:
            relevant = 'felhasznált'
            if possible_materials[0][1]:
                relevant = 'meghatározó'
                
            result = [True, f'A {relevant} alapanyag ({possible_materials[0][0]}) egységára {price_direction[0]}'\
                      f', amely változás eredményezhette az anyagköltséghányad {price_direction[1]}.']
            
        elif len(possible_materials) >= 1:
            possible_materials_list = ''
            for item in possible_materials:
                possible_materials_list += (item[0])
                if item[1]:
                    possible_materials_list += (' / megj.: meghatározó anyag')
                possible_materials_list += (', ')
            possible_materials_list = possible_materials_list[:-2]

            result = [True, f'Több alapanyag ({possible_materials_list}) egységára {price_direction[0]}'\
                      f', amely változás eredményezhette az anyagköltséghányad {price_direction[1]}.']

        return(result)

    def __check_new_supplier(self):
        result = [None,'needed_to_ask']
        return(result)
               
    def __check_supplier_structure(self):
        result = [None,'needed_to_ask']
        return(result)

    def __check_new_and_ceased_material(self):
        result = [None,'']

        new_materials = MaterialRatioAnalysis.remove_goods(self.additional_data['new_materials'], 5)
        ceased_materials = MaterialRatioAnalysis.remove_goods(self.additional_data['ceased_materials'], 5)

        if len(new_materials) == 0 and len(ceased_materials) == 0:
            return [None,'']

        new_materials_list = ''
        for item in new_materials:
            new_materials_list += (item[0] + ', ')
        new_materials_list = new_materials_list[:-2]
        
        ceased_materials_list = ''
        for item in ceased_materials:
            ceased_materials_list += (item[0] + ', ')
        ceased_materials_list = ceased_materials_list[:-2]

        if len(new_materials) == 1 and len(ceased_materials) == 0:
            result[1] = f'A tárgyévben termelésbe került új alapanyag ({new_materials_list})'\
                ' beszerzési ára befolyásolhatta az anyagköltséghányad alakulását.'

        elif len(new_materials) > 1 and len(ceased_materials) == 0:
            result[1] = f'A tárgyévben termelésbe került új alapanyagok ({new_materials_list})'\
                ' beszerzési ára befolyásolhatta az anyagköltséghányad alakulását.'

        elif len(new_materials) == 0 and len(ceased_materials) == 1:
            result[1] = f'A tárgyévi termelésből kieső alapanyag ({ceased_materials_list})'\
                ' korábbi beszerzése befolyásolhatta az anyagköltséghányad alakulását.'
        
        elif len(new_materials) == 0 and len(ceased_materials) > 1:
            result[1] = f'A tárgyévi termelésből kieső alapanyagok ({ceased_materials_list})'\
                ' korábbi beszerzése befolyásolhatta az anyagköltséghányad alakulását.'

        elif len(new_materials) == 1 and len(ceased_materials) == 1:
            result[1] = f'A tárgyévben termelésbe került új ({new_materials_list}),'\
                f' illetve a termelésből kiesett ({ceased_materials_list}) korábbi alapanyag'\
                ' beszerzési ára befolyásolhatta az anyagköltséghányad alakulását.'
            
        else:
            result[1] = f'A tárgyévben termelésbe került új ({new_materials_list}),'\
                f' illetve a termelésből kiesett korábbi ({ceased_materials_list}) alapanyagok'\
                ' beszerzési ára befolyásolhatta az anyagköltséghányad alakulását.'

        return(result)

    def __check_material_structure(self, direction):
        result = [None,'']

        materials = MaterialRatioAnalysis.remove_goods(self.additional_data['materials'], 5)
        relevant_material = self.additional_data['relevant_material']
        materials_quantity_change = MaterialRatioAnalysis.remove_goods(self.additional_data['quantity_change'], 2)

        if len(materials) == 0:
            return [None, 'needed_to_ask']

        materials_quantity_change_temp = materials_quantity_change[::]
        idx_in_original_list = -1
        for idx, item in enumerate(materials_quantity_change_temp): # filtering the irrelevant changes ( -1% < chg < 1% )
            idx_in_original_list += 1
            if item[0] >-1 and item[0] <1:
                materials_quantity_change.pop(idx_in_original_list)
                materials.pop(idx_in_original_list)
                idx_in_original_list -= 1
                if relevant_material[0] and relevant_material[1] == idx:
                    relevant_material[0] = False
                elif relevant_material[0] and relevant_material[1] > idx:
                    relevant_material[1] -= 1
        
        potentional_materials = []
        potentional_materials_change = []
        idx_in_new_list = -1
        relevant_material_idx = -1 # relevant material index in potentional materials
        not_potential_exists = False
        for idx, item in enumerate(materials_quantity_change): # filtering the potential materials
            if (item[0] > 1 and direction == 'increase') or (item[0] < -1 and direction == 'decrease'):
                idx_in_new_list += 1
                potentional_materials_change.append(item)
                if relevant_material[0] and relevant_material[1] == idx:
                    relevant_material_idx = idx_in_new_list
                potentional_materials.append(materials[idx])
            else:
                not_potential_exists = True
        
        potentional_materials_list = ''
        for idx, item in enumerate(potentional_materials):
            potentional_materials_list += (item[0])
            if relevant_material[0] and relevant_material_idx == idx:
                potentional_materials_list += ' / megj.: meghatározó anyag'
            potentional_materials_list += (', ')
        potentional_materials_list = potentional_materials_list[:-2]
        
        relevant = ''
        if direction == 'decrease':
            change_text = ['csökkent', 'javulását', 'növekvő', 'olcsóbb']
        else:
            change_text = ['növekedett', 'emelkedését', 'csökkenő', 'drágább']

        if len(potentional_materials) == 1 and not_potential_exists == False: # only one material is potential, no more materials changed / exists
            if relevant_material_idx == 0:
                relevant = 'meghatározó '
                potentional_materials_list = potentional_materials_list[:-27]
            elif relevant_material_idx != 0 and len(materials) > 0:
                relevant = 'egyik '

            result[1] = f'A termelésben felhasznált {relevant}alapanyag ({potentional_materials_list}) igénybe vett mennyisége {str(potentional_materials_change[0][1])[1:-1]}'\
                f'%-kal {change_text[0]} tárgyvében, amely változás eredményezhette az anyagköltséghányad {change_text[1]}.'

        elif len(potentional_materials) == 1 and not_potential_exists == True: # only one material is potential, but one/more materials changed contraversial
            if relevant_material_idx == 0:
                relevant = 'meghatározó '
                potentional_materials_list = potentional_materials_list[:-27]
            elif relevant_material_idx != 0 and len(materials) > 0:
                relevant = 'egyik '

            result[1] = f'A termelésben felhasznált {relevant}alapanyag ({potentional_materials_list}) igénybe vett mennyisége {str(potentional_materials_change[0][1])[1:-1]}'\
                f'%-kal {change_text[0]} tárgyvében, amely változás - az alapanyag egyéb anyagokhoz viszonyított árszínvonalának függvényében -'\
                f' eredményezhette az anyagköltséghányad {change_text[1]}. Megj.: a {change_text[2]} mennyiségben felhasznált, esetlegesen'\
                f' {change_text[3]} anyagok hasonló változást okozhattak a költséghányadban.'

        elif len(potentional_materials) > 1 and not_potential_exists == False: # more materials are potential, no more materials changed / exists

            result[1] = f'A termelésben felhasznált egyes alapanyagok ({potentional_materials_list}) igénybe vett mennyisége'\
                f' {change_text[0]} tárgyvében, amely változás eredményezhette az anyagköltséghányad {change_text[1]}.'

        elif len(potentional_materials) > 1 and not_potential_exists == True: # more materials are potential, but one/more materials changed contraversial

            result[1] = f'A termelésben felhasznált egyes alapanyagok ({potentional_materials_list}) igénybe vett mennyisége'\
                f' {change_text[0]} tárgyvében, amely változás - az alapanyag egyéb anyagokhoz viszonyított árszínvonalának függvényében -'\
                f' eredményezhette az anyagköltséghányad {change_text[1]}. Megj.: a {change_text[2]} mennyiségben felhasznált, esetlegesen'\
                f' {change_text[3]} anyagok hasonló változást okozhattak a költséghányadban.'

        return(result)

    def __check_own_production_rate(self, direction):
        if not self.base_year:
            return [None,'needed_to_ask']

        chg_semi_finished_base = 0
        if self.base_year.chg_semi_finished > 0:
            chg_semi_finished_base = self.base_year.chg_semi_finished
        chg_semi_finished_actual = 0
        if self.actual_year.chg_semi_finished > 0:
            chg_semi_finished_actual = self.actual_year.chg_semi_finished
        own_work_cap_base = self.base_year.own_work_cap
        own_work_cap_actual = self.actual_year.own_work_cap

        positive_own_work_base_ratio = (chg_semi_finished_base + own_work_cap_base) / self.base_year.production_value # (own work capitalized + increase in semi finished goods) / production value
        positive_own_work_actual_ratio = (chg_semi_finished_actual + own_work_cap_actual) / self.actual_year.production_value
        positive_own_work_actual_ratio_chg = positive_own_work_actual_ratio / positive_own_work_base_ratio

        if positive_own_work_actual_ratio_chg > 1 and direction == 'increase':          
            return [True, 'A pozitív előjelű saját teljesítmények (saját termeléső készletek állománynövekedése és saját előállítású eszközök'\
                    ' aktivált értéke) bruttó teljesítményben mért részaránya emelkedett tárgyévben, amely tényező az anyagköltséghányad'\
                    ' növekedésére hat. (Megj.: ennek oka, hogy ezen tranzakciók bekerülési értéken - tehát az árbevételtől eltérően, árrés nélkül -'\
                    ' könyvelt tételek.)']
        
        elif positive_own_work_actual_ratio_chg < 1 and direction == 'decrease':
            return [True, 'A pozitív előjelű saját teljesítmények (saját termeléső készletek állománynövekedése és saját előállítású eszközök'\
                    ' aktivált értéke) bruttó teljesítményben mért részaránya csökkent tárgyévben, amely tényező az anyagköltséghányad'\
                    ' csökkenésére hat. (Megj.: ennek oka, hogy ezen tranzakciók bekerülési értéken - tehát az árbevételtől eltérően, árrés nélkül -'\
                    ' könyvelt tételek.)']          
        
        return [None,'']

    def __check_new_technology(self):
        result = [None,'needed_to_ask']
        return(result)

    
if __name__ == '__main__':
    
    actual_year = get_findata_from_csv('2021','closed')
    base_year = get_findata_from_csv('2020','closed')
    
    if actual_year:
        print(f'Actual year: {actual_year.year}')
        print(f'Material cost ratio: {actual_year.cost_ratios(ratio = "raw_material_cost")}')
    else:
        print(actual_year)

    if base_year:
        print(f'Base year: {base_year.year}')
        print(f'Material cost ratio: {base_year.cost_ratios(ratio = "raw_material_cost")}')
    else:
        print(base_year)

    additional_data = {
        'comment_on_changes_of_product_revenues': [('a magasabb forgalom ', 'áremelés', ' eredménye'), ('a csökkenő árak', ' okozták', ' azt'), False],
        'products': [('alkatrészek gyártása', 514698, '514 698'), ('egyéb fröccsöntött termékek gyártása', 463228, '463 228'), ('szerszámértékesítés', 51469, '51 469')],
        'products_base': [('alkatrészek gyártása', 456500, '456 500'), ('egyéb fröccsöntött termékek gyártása', 375113, '375 113'), ('szerszámértékesítés', 48050, '48 050')],
        'changed_products': ['a növekedés mértéke az árbevételhez mérten nem meghatározó', 'a növekedés az árbevételhez mérten is számottevő mértékű', False],
        'new_products': [('mérnöki tevékenység', 20000, '20 000'), ('gégecsõ gyártása', 10000, '10 000')],
        'ceased_products': [('kereskedelmi tevékenység', 20000, '20 000'), ('ingatlan bérbeadás', 10000, '10 000')],
        'materials': False,
        'relevant_material': [True, 0],
        'materials_unit_cost_change': [(-3.8, '-3.8%', 'N'), (6.2, '+6.2%', 'I'), (-5.6, '+5.6%', 'N')],
        'new_materials': [('PVC', 20000, '20 000', 1000, '1 000', 'N')],
        'ceased_materials': [('bakelit', 20000, '20 000', 1000, '1 000', 'N')],
        'quantity_change': [(4.0, '+4.0%', 'N'), (60.0, '+60.0%', 'I'), (-5.3, '-5.3%', 'N')]
    }

    raw_mat_engine = MaterialRatioAnalysis (actual_year, base_year, additional_data)
    raw_mat_analysis, reasons_dict, reasons_dict_key_order, to_ask_dict, to_ask_dict_key_order  = raw_mat_engine.analyse()
      
    print('\n' + raw_mat_analysis, '\n')
    for key in reasons_dict_key_order:
        print(reasons_dict[key], '\n')
    
    for idx, key in enumerate(to_ask_dict_key_order):
        if idx == 0:
            print('Az anyagköltséghányad változására ezen felül az alábbi tényezők hathattak:')
        print('-', to_ask_dict[key])

        # 'comment_on_changes_of_product_revenues': [('a magasabb forgalom ', 'áremelés', ' eredménye'), ('a csökkenő árak', ' okozták', ' azt'), False],
        # 'products': [('alkatrészek gyártása', 514698, '514 698'), ('egyéb fröccsöntött termékek gyártása', 463228, '463 228'), ('szerszámértékesítés', 51469, '51 469')],
        # 'products_base': [('alkatrészek gyártása', 456500, '456 500'), ('egyéb fröccsöntött termékek gyártása', 375113, '375 113'), ('szerszámértékesítés', 48050, '48 050')],
        # 'changed_products': ['a növekedés mértéke az árbevételhez mérten nem meghatározó', 'a növekedés az árbevételhez mérten is számottevő mértékű', False],
        # 'new_products': [('mérnöki tevékenység', 20000, '20 000'), ('gégecsõ gyártása', 10000, '10 000')],
        # 'ceased_products': [('kereskedelmi tevékenység', 20000, '20 000'), ('ingatlan bérbeadás', 10000, '10 000')],
        # 'materials': [('polietilén granulátum', 260000, '260 000', 26000, '26 000', 'N'), ('alvállalkozói gyártás', 173236, '173 236', 8000, '8 000', 'I'), ('polipropilén granulátum', 170000, '170 000', 18000, '18 000', 'N')],
        # 'relevant_material': [True, 0],
        # 'materials_unit_cost_change': [(-3.8, '-3.8%', 'N'), (6.2, '+6.2%', 'I'), (-5.6, '+5.6%', 'N')],
        # 'new_materials': [('PVC', 20000, '20 000', 1000, '1 000', 'N')],
        # 'ceased_materials': [('bakelit', 20000, '20 000', 1000, '1 000', 'N')],
        # 'quantity_change': [(4.0, '+4.0%', 'N'), (60.0, '+60.0%', 'I'), (-5.3, '-5.3%', 'N')]
